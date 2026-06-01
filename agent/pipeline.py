# ============================================================
# Full Pipeline Orchestrator
# Agent 1 → Slim → Agent 2 → DMN → Route → Audit Log
# ============================================================

import json
from datetime import datetime, timezone

from models import VendorRiskAssessment, DataCompleteness
from agent1 import evaluate_vendor, slim_for_agent2
from agent2_mock import audit_vendor
from dmn_engine import evaluate_dmn, route_to_ai_recommendation
from audit_logger import write_audit_entry, clear_audit_trail


# ============================================================
# Vendor Headquarters Mock (for geographic bias tracking)
# ============================================================

MOCK_HEADQUARTERS = {
    "clearpath logistics": "Netherlands",
    "nexus global holdings": "Panama",
    "partialdata corp": "Germany",
    "borderline safe inc": "United States",
    "conflict industries": "United Kingdom",
    "asdfghjkl corp": "Unknown",
    "uncertain ventures": "Singapore",
    "sneaky risk ltd": "Cayman Islands",
}


# ============================================================
# Pipeline Execution
# ============================================================

def process_vendor(vendor_name: str, use_react: bool = False) -> dict:
    """
    Full pipeline:
    1. Agent 1 evaluates vendor (gather + score)
    2. Slim output for Agent 2
    3. Agent 2 audits red flags
    4. DMN evaluates route
    5. Write audit trail
    6. Return full result
    """
    result = {
        "vendor_name": vendor_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent1": None,
        "slimmed": None,
        "agent2": None,
        "dmn": None,
        "final_route": None,
        "audit_logged": False,
        "error": None,
    }

    try:
        # ---- STEP 1: Agent 1 Evaluation ----
        assessment = evaluate_vendor(vendor_name, use_react=use_react)
        result["agent1"] = assessment.model_dump()

        # ---- STEP 2: Slim for Agent 2 ----
        slimmed = slim_for_agent2(assessment)
        result["slimmed"] = slimmed

        # ---- STEP 3: Agent 2 Audit ----
        agent2_result = audit_vendor(slimmed)
        result["agent2"] = agent2_result.to_dict()

        # ---- STEP 4: DMN Gateway ----
        dmn_result = evaluate_dmn(assessment)
        result["dmn"] = dmn_result

        # Determine final route
        # If Agent 2 recommends escalate AND DMN doesn't already escalate, upgrade
        final_route = dmn_result["route"]
        if agent2_result.auditor_recommendation == "escalate" and final_route != "escalate":
            final_route = "escalate"
            result["dmn"]["route"] = "escalate"
            result["dmn"]["reason"] += " | Upgraded by Agent 2 escalation recommendation"

        result["final_route"] = final_route

        # ---- STEP 5: Audit Log ----
        headquarters = MOCK_HEADQUARTERS.get(
            vendor_name.lower().strip(), "Unknown"
        )

        audit_entry = write_audit_entry(
            vendor_name=assessment.vendor_name,
            vendor_headquarters_country=headquarters,
            risk_score=assessment.risk_score,
            red_flags=assessment.red_flags,
            data_completeness=assessment.data_completeness,
            predictive_multiplicity_flag=assessment.predictive_multiplicity_flag,
            conflicting_data=assessment.conflicting_data,
            ai_recommendation=route_to_ai_recommendation(final_route),
            route_taken=final_route,
            agent_1_model=assessment.agent_1_model,
        )
        result["audit_logged"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


# ============================================================
# CLI Pipeline Runner
# ============================================================

if __name__ == "__main__":
    # Clear previous audit trail for clean test run
    clear_audit_trail()

    test_vendors = [
        "ClearPath Logistics",
        "Nexus Global Holdings",
        "ErrorTrigger Inc.",
        "PartialData Corp",
        "Conflict Industries",
        "asdfghjkl corp",
        "Uncertain Ventures",
        "Sneaky Risk Ltd",
    ]

    print(f"{'='*70}")
    print(f"  THIRD-PARTY RISK GATE — FULL PIPELINE EXECUTION")
    print(f"{'='*70}\n")

    for vendor in test_vendors:
        print(f"\n{'─'*70}")
        print(f"  VENDOR: {vendor}")
        print(f"{'─'*70}")

        result = process_vendor(vendor)

        if result["error"]:
            print(f"  ❌ ERROR: {result['error']}")
            continue

        # Agent 1 Summary
        a1 = result["agent1"]
        print(f"  📊 Agent 1 Score: {a1['risk_score']}")
        print(f"  📦 Data Completeness: {a1['data_completeness']}")
        print(f"  🚩 Red Flags: {a1['red_flags'] if a1['red_flags'] else 'None'}")
        print(f"  ⚡ Multiplicity: {a1['predictive_multiplicity_flag']}")
        print(f"  🆕 New Entity: {a1['new_entity_no_history']}")
        print(f"  ⚠️  Conflicting: {a1['conflicting_data']}")

        # Agent 2 Summary
        a2 = result["agent2"]
        print(f"\n  🔍 Agent 2 Audit:")
        for vf in a2["verified_flags"]:
            icon = "✅" if vf["status"] == "verified" else "❓" if vf["status"] == "unverified" else "❌"
            print(f"     {icon} {vf['flag']}: {vf['status']}")
        print(f"     Confidence: {a2['auditor_confidence']:.2f}")
        print(f"     Recommendation: {a2['auditor_recommendation']}")

        # DMN Route
        dmn = result["dmn"]
        route_icon = "🟢" if dmn["route"] == "auto_approve" else "🟡" if dmn["route"] == "human_review" else "🔴"
        print(f"\n  {route_icon} FINAL ROUTE: {dmn['route'].upper()} (Priority {dmn['priority']})")
        print(f"     Reason: {dmn['reason']}")

        # Audit
        print(f"  📝 Audit Logged: {'✅' if result['audit_logged'] else '❌'}")

    # Print audit trail summary
    from audit_logger import read_audit_trail
    trail = read_audit_trail()

    print(f"\n{'='*70}")
    print(f"  AUDIT TRAIL: {len(trail)} entries written")
    print(f"{'='*70}\n")

    for entry in trail:
        print(f"  {entry['timestamp'][:19]} | {entry['vendor_name'][:30]:<30} | Score: {entry['risk_score']:>3} | Route: {entry['route_taken']:<15} | HQ: {entry['vendor_headquarters_country']}")
