# ============================================================
# Audit Logger — Immutable Audit Trail
# Writes to local JSON file (simulates Orchestrator Queue Items)
# ============================================================

import json
import os
from datetime import datetime, timezone
from models import AuditTrailEntry, DataCompleteness


AUDIT_LOG_FILE = "audit_trail.jsonl"  # JSON Lines format — append-only


def write_audit_entry(
    vendor_name: str,
    vendor_headquarters_country: str,
    risk_score: int,
    red_flags: list,
    data_completeness: DataCompleteness,
    predictive_multiplicity_flag: bool,
    conflicting_data: bool,
    ai_recommendation: str,
    route_taken: str,
    agent_1_model: str = "gpt-4o-2024-08-06",
    agent_2_model: str = "claude-3-5-sonnet-20241022",
    human_decision: str = None,
    human_reviewer: str = None,
    override_flag: bool = False,
    override_justification: str = None,
) -> AuditTrailEntry:
    """
    Creates and writes an immutable audit trail entry.
    In production: writes to UiPath Orchestrator Queue Items.
    In development: writes to local JSONL file.
    """
    entry = AuditTrailEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        vendor_name=vendor_name,
        vendor_headquarters_country=vendor_headquarters_country,
        risk_score=risk_score,
        red_flags=red_flags,
        data_completeness=data_completeness,
        predictive_multiplicity_flag=predictive_multiplicity_flag,
        conflicting_data=conflicting_data,
        ai_recommendation=ai_recommendation,
        route_taken=route_taken,
        human_decision=human_decision,
        human_reviewer=human_reviewer,
        override_flag=override_flag,
        override_justification=override_justification,
        agent_1_model=agent_1_model,
        agent_2_model=agent_2_model,
    )

    # Append to JSONL file (one JSON object per line)
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry.model_dump_json() + "\n")

    return entry


def read_audit_trail() -> list:
    """Reads all audit trail entries from the JSONL file."""
    entries = []
    if not os.path.exists(AUDIT_LOG_FILE):
        return entries

    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def query_overrides() -> list:
    """Returns all entries where human overrode AI recommendation."""
    entries = read_audit_trail()
    return [e for e in entries if e.get("override_flag") == True]


def clear_audit_trail():
    """Clears the audit trail file. Use only in testing."""
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)
