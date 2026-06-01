from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum
from datetime import datetime


class DataCompleteness(str, Enum):
    full = "full"
    partial = "partial"
    none = "none"


class VendorRiskAssessment(BaseModel):
    vendor_name: str
    reasoning: str                              # Chain-of-thought ordering: MUST be before risk_score
    risk_score: int = Field(ge=0, le=100)
    red_flags: List[str]
    data_sources_used: List[str]
    data_completeness: DataCompleteness
    conflicting_data: bool
    predictive_multiplicity_flag: bool = False
    new_entity_no_history: bool = False         # Adversarial robustness flag
    agent_1_model: str = "gpt-4o-2024-08-06"


class AuditTrailEntry(BaseModel):
    timestamp: datetime
    vendor_name: str
    vendor_headquarters_country: str
    risk_score: int
    red_flags: List[str]
    data_completeness: DataCompleteness
    predictive_multiplicity_flag: bool
    conflicting_data: bool
    ai_recommendation: Literal["auto_approve", "human_review", "escalate"]
    route_taken: Literal["auto_approve", "human_review", "escalate"]
    human_decision: Optional[Literal["approve", "reject"]] = None
    human_reviewer: Optional[str] = None
    override_flag: bool = False
    override_justification: Optional[str] = None
    agent_1_model: str = "gpt-4o-2024-08-06"
    agent_2_model: str = "claude-3-5-sonnet-20241022"
