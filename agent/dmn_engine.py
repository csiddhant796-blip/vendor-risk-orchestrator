# ============================================================
# DMN Gateway Engine — PRIORITY Hit Policy
# Implements the 9-row decision table from ARCHITECTURE.md
# ============================================================

from models import VendorRiskAssessment, DataCompleteness
from typing import Literal

RouteType = Literal["escalate", "human_review", "auto_approve"]


def evaluate_dmn(assessment: VendorRiskAssessment) -> dict:
    """
    Evaluates the DMN gateway table with PRIORITY hit policy.
    Returns the highest-priority matching route.
    
    Priority 1 (Highest) → Escalate
    Priority 2-8 → Human Review
    Priority 9 (Lowest) → Auto-Approve
    
    Returns: {
        "route": "escalate" | "human_review" | "auto_approve",
        "priority": int,
        "reason": str
    }
    """
    score = assessment.risk_score
    flags = assessment.red_flags
    completeness = assessment.data_completeness
    multiplicity = assessment.predictive_multiplicity_flag
    new_entity = assessment.new_entity_no_history
    conflicting = assessment.conflicting_data

    # Priority 1: Any red flags → Escalate
    if flags and len(flags) > 0:
        return {
            "route": "escalate",
            "priority": 1,
            "reason": f"Red flags present: {flags}"
        }

    # Priority 2: Predictive multiplicity → Human Review
    if multiplicity:
        return {
            "route": "human_review",
            "priority": 2,
            "reason": "Predictive multiplicity flag triggered (delta > 15)"
        }

    # Priority 3: New entity with no history → Human Review
    if new_entity:
        return {
            "route": "human_review",
            "priority": 3,
            "reason": "New entity with no operational history detected"
        }

    # Priority 4: Conflicting data → Human Review
    if conflicting:
        return {
            "route": "human_review",
            "priority": 4,
            "reason": "Conflicting data detected across sources"
        }

    # Priority 5: Partial data → Human Review
    if completeness == DataCompleteness.partial:
        return {
            "route": "human_review",
            "priority": 5,
            "reason": "Partial data completeness — some sources unavailable"
        }

    # Priority 6: No data → Human Review
    if completeness == DataCompleteness.none:
        return {
            "route": "human_review",
            "priority": 6,
            "reason": "No data available from any source"
        }

    # Priority 7: Score > 70, full data, no flags → Human Review
    if score > 70 and completeness == DataCompleteness.full:
        return {
            "route": "human_review",
            "priority": 7,
            "reason": f"High risk score ({score}) with full data"
        }

    # Priority 8: Score 30-70, full data, no flags → Human Review
    if 30 <= score <= 70 and completeness == DataCompleteness.full:
        return {
            "route": "human_review",
            "priority": 8,
            "reason": f"Moderate risk score ({score}) — requires human judgment"
        }

    # Priority 9: Score < 30, full data, no flags → Auto-Approve
    if score < 30 and completeness == DataCompleteness.full:
        return {
            "route": "auto_approve",
            "priority": 9,
            "reason": f"Low risk score ({score}), full data, no flags"
        }

    # Default fallback — should never reach here if DMN table is complete
    return {
        "route": "human_review",
        "priority": 0,
        "reason": "Default fallback — no DMN rule matched"
    }


def route_to_ai_recommendation(route: str) -> str:
    """Converts DMN route to ai_recommendation field value."""
    mapping = {
        "escalate": "escalate",
        "human_review": "human_review",
        "auto_approve": "auto_approve",
    }
    return mapping.get(route, "human_review")
