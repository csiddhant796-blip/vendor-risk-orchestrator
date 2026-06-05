"""
pipeline_server.py
==================
Drop this into the agent/ directory (alongside pipeline.py and mock_server.py).
Exposes process_vendor() over HTTP so UiPath Maestro can call it via
"Execute HTTP request" in a Service Task.

HOW TO RUN (both servers must be running before Maestro calls this):

    # Terminal 1 — mock data source (already your existing server)
    cd agent
    python mock_server.py

    # Terminal 2 — THIS server (pipeline wrapper)
    cd agent
    python pipeline_server.py

Then tunnel it (in Terminal 3):
    ngrok http 9000
    # OR (no account needed):
    # cloudflared tunnel --url http://localhost:9000

Paste the HTTPS tunnel URL into Maestro's Service Task.

NOTE: Swarup should verify the field names below match what process_vendor()
actually returns before running. This is derived from the published data
contract in the handoff (models.py VendorRiskAssessment).
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# pipeline.py must be in the same directory as this file
from pipeline import process_vendor

app = FastAPI(
    title="Vendor Risk Pipeline API",
    description="Adversarial dual-agent vendor due-diligence pipeline for Themis/UiPath Maestro",
    version="1.0.0",
)


# ── Response schema ──────────────────────────────────────────────────────────
# These are the fields the Maestro DMN_Risk_Gate Script task needs.
# Derived from VendorRiskAssessment in models.py.

class PipelineResponse(BaseModel):
    vendor_name: str
    risk_score: int                   # 0–100 from Agent 1
    has_red_flags: bool               # derived: len(red_flags) > 0
    data_completeness: str            # "full" | "partial" | "none"
    conflicting_data: bool
    predictive_multiplicity_flag: bool
    new_entity_no_history: bool
    pipeline_route: str               # pipeline's own DMN result (cross-check)
    red_flags: list                   # raw list — useful for the audit trail / demo narration


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Quick liveness check — Maestro or you can call this to confirm the server is up."""
    return {"status": "ok", "service": "vendor-risk-pipeline"}


@app.get("/assess/{vendor_name}", response_model=PipelineResponse)
def assess_vendor(vendor_name: str):
    """
    Run the full pipeline: Agent 1 (high recall) → slimming → Agent 2 (high precision)
    → 9-rule DMN → audit trail.

    Returns the risk fields Maestro needs to feed into the DMN_Risk_Gate Script task.

    Example: GET /assess/ClearPath%20Logistics
    """
    try:
        result = process_vendor(vendor_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")

    # ── Extract Agent 1 assessment ──────────────────────────────────────────
    # process_vendor() returns a dict; agent1 value may be a Pydantic model
    # or a plain dict depending on pipeline.py implementation.
    agent1_raw = result.get("agent1", {})

    # Handle Pydantic model instance
    if hasattr(agent1_raw, "risk_score"):
        risk_score              = int(agent1_raw.risk_score)
        red_flags               = list(agent1_raw.red_flags or [])
        data_completeness       = str(agent1_raw.data_completeness or "partial")
        conflicting_data        = bool(agent1_raw.conflicting_data)
        pred_mult_flag          = bool(agent1_raw.predictive_multiplicity_flag)
        new_entity_flag         = bool(agent1_raw.new_entity_no_history)
    # Handle plain dict (e.g. if pipeline already serialised it)
    elif isinstance(agent1_raw, dict):
        risk_score              = int(agent1_raw.get("risk_score", 50))
        red_flags               = list(agent1_raw.get("red_flags", []))
        data_completeness       = str(agent1_raw.get("data_completeness", "partial"))
        conflicting_data        = bool(agent1_raw.get("conflicting_data", False))
        pred_mult_flag          = bool(agent1_raw.get("predictive_multiplicity_flag", False))
        new_entity_flag         = bool(agent1_raw.get("new_entity_no_history", False))
    else:
        # Fallback — shouldn't happen, but safe default so Maestro always gets a valid response
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected agent1 type: {type(agent1_raw)}. Check pipeline.py return structure."
        )

    return PipelineResponse(
        vendor_name=vendor_name,
        risk_score=risk_score,
        has_red_flags=len(red_flags) > 0,
        data_completeness=data_completeness,
        conflicting_data=conflicting_data,
        predictive_multiplicity_flag=pred_mult_flag,
        new_entity_no_history=new_entity_flag,
        pipeline_route=str(result.get("final_route", "human_review")),
        red_flags=red_flags,
    )


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting Vendor Risk Pipeline Server on http://0.0.0.0:9000")
    print("Make sure mock_server.py is already running on :8000")
    uvicorn.run(app, host="0.0.0.0", port=9000)
