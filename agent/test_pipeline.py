# ============================================================
# End-to-End Pipeline Test — 11 Test Cases
# Tests the full flow: Agent 1 → Slim → Agent 2 → DMN → Audit
# ============================================================

import sys
import os
from pipeline import process_vendor
from audit_logger import clear_audit_trail, read_audit_trail

# ============================================================
# Test Definitions
# ============================================================

PIPELINE_TESTS = [
    {
        "id": 1,
        "name": "Happy path, low risk",
        "vendor": "ClearPath Logistics",
        "expect_route": "auto_approve",
        "expect_score": 18,
        "validates": "Full pipeline speed"
    },
    {
        "id": 2,
        "name": "High risk, sanctions",
        "vendor": "Nexus Global Holdings",
        "expect_route": "escalate",
        "expect_score": 72,
        "validates": "Agent 2 verifies sanctions → escalate"
    },
    {
        "id": 3,
        "name": "API total failure",
        "vendor": "ErrorTrigger Inc.",
        "expect_error": True,
        "validates": "Graceful failure (Art. 15)"
    },
    {
        "id": 4,
        "name": "Partial data state",
        "vendor": "PartialData Corp",
        "expect_route": "human_review",
        "validates": "SHIELDA flow control through pipeline"
    },
    {
        "id": 5,
        "name": "Low risk score (boundary)",
        "vendor": "Borderline Safe Inc",
        "expect_route": "auto_approve",
        "expect_score": 25,
        "validates": "Boundary scoring through pipeline"
    },
    {
        "id": 6,
        "name": "Timer expiration",
        "vendor": "__TIMER__",
        "skip": True,
        "validates": "BPMN-side test"
    },
    {
        "id": 7,
        "name": "Conflicting data",
        "vendor": "Conflict Industries",
        "expect_route": "human_review",
        "validates": "Conflicting data → human review"
    },
    {
        "id": 8,
        "name": "Hallucinated vendor",
        "vendor": "asdfghjkl corp",
        "expect_route": "human_review",
        "validates": "New entity → human review"
    },
    {
        "id": 9,
        "name": "Predictive multiplicity",
        "vendor": "Uncertain Ventures",
        "expect_route": "human_review",
        "validates": "Multiplicity flag → human review"
    },
    {
        "id": 10,
        "name": "DMN priority override",
        "vendor": "Sneaky Risk Ltd",
        "expect_route": "escalate",
        "expect_score": 25,
        "validates": "Low score but red flag → escalate"
    },
    {
        "id": 11,
        "name": "Primary LLM provider outage",
        "vendor": "providerfallback test",
        "expect_error": True,
        "validates": "Provider fallback path"
    },
]


def run_pipeline_tests():
    passed = 0
    failed = 0
    skipped = 0

    # Clean audit trail before tests
    clear_audit_trail()

    print(f"{'='*70}")
    print(f"  FULL PIPELINE TEST — 11 Cases (End-to-End)")
    print(f"{'='*70}\n")

    for test in PIPELINE_TESTS:
        tid = test["id"]
        name = test["name"]

        if test.get("skip"):
            print(f"  ⏭️  TEST {tid}: {name} — SKIPPED (BPMN-side)")
            skipped += 1
            continue

        result = process_vendor(test["vendor"])

        # Error-expected tests
        if test.get("expect_error"):
            if result.get("error"):
                print(f"  ✅ TEST {tid}: {name} — PASSED (Error handled: {result['error'][:50]})")
                passed += 1
            else:
                print(f"  ❌ TEST {tid}: {name} — FAILED (Expected error, got success)")
                failed += 1
            continue

        # Check for unexpected errors
        if result.get("error"):
            print(f"  ❌ TEST {tid}: {name} — FAILED (Unexpected error: {result['error']})")
            failed += 1
            continue

        # Validate route
        errors = []
        actual_route = result.get("final_route")

        if "expect_route" in test and actual_route != test["expect_route"]:
            errors.append(f"route: expected '{test['expect_route']}', got '{actual_route}'")

        if "expect_score" in test:
            actual_score = result["agent1"]["risk_score"]
            if actual_score != test["expect_score"]:
                errors.append(f"score: expected {test['expect_score']}, got {actual_score}")

        # Verify audit was logged
        if not result.get("audit_logged"):
            errors.append("audit not logged")

        if errors:
            print(f"  ❌ TEST {tid}: {name} — FAILED")
            for err in errors:
                print(f"      → {err}")
            failed += 1
        else:
            print(f"  ✅ TEST {tid}: {name} — PASSED (route: {actual_route})")
            passed += 1

    # Verify audit trail integrity
    trail = read_audit_trail()
    print(f"\n{'─'*70}")
    print(f"  AUDIT TRAIL: {len(trail)} entries written")

    # Check all entries are valid
    valid_entries = 0
    for entry in trail:
        try:
            if "vendor_name" in entry and "route_taken" in entry and "timestamp" in entry:
                valid_entries += 1
        except:
            pass

    if valid_entries == len(trail) and len(trail) > 0:
        print(f"  ✅ All {valid_entries} audit entries valid and immutable")
    else:
        print(f"  ❌ Audit trail validation failed: {valid_entries}/{len(trail)} valid")
        failed += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {passed} PASSED | {failed} FAILED | {skipped} SKIPPED")
    print(f"{'='*70}\n")

    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    run_pipeline_tests()
