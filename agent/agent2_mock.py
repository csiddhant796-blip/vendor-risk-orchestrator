# ============================================================
# Agent 2 Mock: Evidence/Auditor (Yin)
# Simulates Claude 3.5 Sonnet via UiPath Agent Builder
# ============================================================

import json
from typing import List, Literal


class VerifiedFlag:
    def __init__(self, flag: str, status: str, evidence: str, source: str):
        self.flag = flag
        self.status = status  # "verified" | "unverified" | "contradicted"
        self.evidence = evidence
        self.source = source

    def to_dict(self):
        return {
            "flag": self.flag,
            "status": self.status,
            "evidence": self.evidence,
            "source": self.source
        }


class Agent2Result:
    def __init__(
        self,
        vendor_name: str,
        verified_flags: List[VerifiedFlag],
        new_flags_discovered: List[str],
        score_assessment: str,
        score_assessment_reasoning: str,
        auditor_recommendation: str,
        auditor_confidence: float,
    ):
        self.vendor_name = vendor_name
        self.verified_flags = verified_flags
        self.new_flags_discovered = new_flags_discovered
        self.score_assessment = score_assessment
        self.score_assessment_reasoning = score_assessment_reasoning
        self.auditor_recommendation = auditor_recommendation
        self.auditor_confidence = auditor_confidence

    def to_dict(self):
        return {
            "vendor_name": self.vendor_name,
            "verified_flags": [f.to_dict() for f in self.verified_flags],
            "new_flags_discovered": self.new_flags_discovered,
            "score_assessment": self.score_assessment,
            "score_assessment_reasoning": self.score_assessment_reasoning,
            "auditor_recommendation": self.auditor_recommendation,
            "auditor_confidence": self.auditor_confidence,
        }


# ============================================================
# Mock Verification Database
# Simulates what Agent 2 would find when independently checking
# ============================================================

MOCK_VERIFICATION_DB = {
    "sanctions_list_match": {
        "verifiable": True,
        "evidence": "Entity appears on OFAC Specially Designated Nationals list, entry dated 2024-11-15. Alias 'Nexus Global Ltd' also listed.",
        "source": "OFAC SDN Database"
    },
    "negative_news": {
        "verifiable": True,
        "evidence": "Reuters article dated 2025-01-20: 'Nexus Global Holdings fined $2.3M for regulatory violations in EU jurisdictions.'",
        "source": "Reuters News Archive"
    },
    "regulatory_violations": {
        "verifiable": True,
        "evidence": "EU regulatory filing shows 3 separate violation citations between 2023-2025.",
        "source": "EU Regulatory Database"
    },
    "bankruptcy_filing": {
        "verifiable": True,
        "evidence": "Court filing shows Chapter 11 bankruptcy petition filed 2025-02-10.",
        "source": "Public Court Records"
    },
    "fraud_allegations": {
        "verifiable": False,
        "evidence": "No evidence found",
        "source": "N/A"
    },
    "data_breach_history": {
        "verifiable": False,
        "evidence": "No evidence found",
        "source": "N/A"
    },
}


def audit_vendor(slimmed_data: dict) -> Agent2Result:
    """
    Mock Agent 2 audit.
    Receives slimmed data (no reasoning, no narrative).
    Independently verifies each red flag.
    """
    vendor_name = slimmed_data.get("vendor_name", "Unknown")
    risk_score = slimmed_data.get("risk_score", 0)
    red_flags = slimmed_data.get("red_flags", [])
    data_sources = slimmed_data.get("data_sources_used", [])
    completeness = slimmed_data.get("data_completeness", "none")

    # Step 1: Verify each red flag independently
    verified_flags = []
    any_verified_disqualifying = False

    for flag in red_flags:
        db_entry = MOCK_VERIFICATION_DB.get(flag, {
            "verifiable": False,
            "evidence": "No evidence found",
            "source": "N/A"
        })

        if db_entry["verifiable"]:
            status = "verified"
            any_verified_disqualifying = True
        else:
            status = "unverified"

        verified_flags.append(VerifiedFlag(
            flag=flag,
            status=status,
            evidence=db_entry["evidence"],
            source=db_entry["source"]
        ))

    # Step 2: Determine confidence
    if completeness == "none":
        confidence = 0.2
    elif completeness == "partial":
        confidence = 0.4
    elif len(data_sources) == 0:
        confidence = 0.3
    elif any_verified_disqualifying:
        confidence = 0.95
    else:
        confidence = 0.8

    # Step 3: Score assessment
    if risk_score > 70 and any_verified_disqualifying:
        score_assessment = "score_justified"
        score_reasoning = f"Score {risk_score} is justified — verified disqualifying flags present."
    elif risk_score < 30 and not any_verified_disqualifying:
        score_assessment = "score_justified"
        score_reasoning = f"Score {risk_score} is justified — no verified disqualifying flags."
    elif risk_score < 30 and any_verified_disqualifying:
        score_assessment = "score_too_low"
        score_reasoning = f"Score {risk_score} is too low — verified disqualifying flags were found."
    else:
        score_assessment = "score_justified"
        score_reasoning = f"Score {risk_score} is within acceptable range given evidence."

    # Step 4: Recommendation
    if any_verified_disqualifying:
        recommendation = "escalate"
    elif confidence < 0.6:
        recommendation = "request_more_data"
    else:
        recommendation = "confirm"

    return Agent2Result(
        vendor_name=vendor_name,
        verified_flags=verified_flags,
        new_flags_discovered=[],  # Mock doesn't discover new flags
        score_assessment=score_assessment,
        score_assessment_reasoning=score_reasoning,
        auditor_recommendation=recommendation,
        auditor_confidence=confidence,
    )
