from fastapi import FastAPI, HTTPException
from models import VendorRiskAssessment, DataCompleteness
import uvicorn

app = FastAPI(title="Third-Party Risk Gate Mock API")

# ============================================================
# SEED DATA: 11 test scenarios mapped to test matrix
# ============================================================

MOCK_VENDORS = {
    # Test 1: Happy path, low risk
    "clearpath logistics": VendorRiskAssessment(
        vendor_name="ClearPath Logistics",
        reasoning="No negative signals detected. Company has 5+ years of clean operational history. No sanctions, no negative news, full registry data.",
        risk_score=18,
        red_flags=[],
        data_sources_used=["OpenCorporates", "NewsAPI"],
        data_completeness=DataCompleteness.full,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 2: High risk, sanctions
    "nexus global holdings": VendorRiskAssessment(
        vendor_name="Nexus Global Holdings",
        reasoning="Vendor found on secondary sanctions watch list. Negative news detected regarding regulatory violations in 3 jurisdictions. Corporate registry shows multiple subsidiary restructuring events.",
        risk_score=72,
        red_flags=["sanctions_list_match", "negative_news"],
        data_sources_used=["OpenCorporates", "NewsAPI"],
        data_completeness=DataCompleteness.full,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 4: Partial data state
    "partialdata corp": VendorRiskAssessment(
        vendor_name="PartialData Corp",
        reasoning="OpenCorporates returned valid data. NewsAPI timed out. Limited assessment possible based on available data.",
        risk_score=45,
        red_flags=[],
        data_sources_used=["OpenCorporates"],
        data_completeness=DataCompleteness.partial,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 5: Low risk score but human overrides AI
    "borderline safe inc": VendorRiskAssessment(
        vendor_name="Borderline Safe Inc",
        reasoning="Vendor appears low risk based on available data. Clean registry, no negative news. However, operational history is only 2 years.",
        risk_score=25,
        red_flags=[],
        data_sources_used=["OpenCorporates", "NewsAPI"],
        data_completeness=DataCompleteness.full,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 7: Conflicting data
    "conflict industries": VendorRiskAssessment(
        vendor_name="Conflict Industries",
        reasoning="OpenCorporates shows company status as 'Active'. NewsAPI reports company filed for bankruptcy 3 months ago. Data sources contradict each other.",
        risk_score=60,
        red_flags=[],
        data_sources_used=["OpenCorporates", "NewsAPI"],
        data_completeness=DataCompleteness.full,
        conflicting_data=True,
        predictive_multiplicity_flag=False,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 8: Hallucinated / unknown vendor
    "asdfghjkl corp": VendorRiskAssessment(
        vendor_name="asdfghjkl corp",
        reasoning="No data found in any source. Vendor does not appear in corporate registries or news databases. Likely a fabricated or misspelled entity name.",
        risk_score=0,
        red_flags=[],
        data_sources_used=[],
        data_completeness=DataCompleteness.none,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=True,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 9: Predictive multiplicity trigger
    "uncertain ventures": VendorRiskAssessment(
        vendor_name="Uncertain Ventures",
        reasoning="Model produced highly variable scores across evaluation runs. Some runs flagged potential compliance issues, others did not. High uncertainty in assessment.",
        risk_score=55,
        red_flags=[],
        data_sources_used=["OpenCorporates", "NewsAPI"],
        data_completeness=DataCompleteness.full,
        conflicting_data=False,
        predictive_multiplicity_flag=True,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),

    # Test 10: DMN priority override (low score but has red flag)
    "sneaky risk ltd": VendorRiskAssessment(
        vendor_name="Sneaky Risk Ltd",
        reasoning="Overall risk score is low based on operational metrics. However, a sanctions watch list match was detected during screening.",
        risk_score=25,
        red_flags=["sanctions_list_match"],
        data_sources_used=["OpenCorporates", "NewsAPI"],
        data_completeness=DataCompleteness.full,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=False,
        agent_1_model="gpt-4o-2024-08-06"
    ),
}


@app.get("/assess_vendor/{vendor_name}", response_model=VendorRiskAssessment)
def assess_vendor(vendor_name: str):
    """
    Mock endpoint for Agent 1 data gathering.
    Returns deterministic responses for seed vendors.
    """
    key = vendor_name.lower().strip()

    # Test 3: API total failure
    if key == "errortrigger inc.":
        raise HTTPException(status_code=503, detail="External API unavailable")

    # Test 11: Primary LLM provider outage (simulated via header check in real impl)
    if key == "providerfallback test":
        raise HTTPException(status_code=500, detail="Primary LLM provider 5xx error")

    # Known vendor
    if key in MOCK_VENDORS:
        return MOCK_VENDORS[key]

    # Unknown vendor — triggers new_entity_no_history
    return VendorRiskAssessment(
        vendor_name=vendor_name,
        reasoning=f"No data found for '{vendor_name}' in any source. Vendor not found in corporate registries or news databases.",
        risk_score=0,
        red_flags=[],
        data_sources_used=[],
        data_completeness=DataCompleteness.none,
        conflicting_data=False,
        predictive_multiplicity_flag=False,
        new_entity_no_history=True,
        agent_1_model="gpt-4o-2024-08-06"
    )


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Third-Party Risk Gate Mock API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
