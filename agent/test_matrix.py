# ============================================================
# Automated Test Matrix — 11 Test Cases
# ============================================================

import httpx
import json
import sys
from models import VendorRiskAssessment, DataCompleteness

MOCK_BASE = "http://localhost:8000"

# ============================================================
# Test Definitions
# ============================================================

TESTS = [
    {
        "id": 1,
        "name": "Happy path, low risk",
        "vendor": "ClearPath Logistics",
        "expect_score": 18,
        "expect_completeness": "full",
        "expect_red_flags_empty": True,
        "expect_path": "Auto-Approve",
        "validates": "Speed and efficiency"
    },
    {
        "id": 2,
        "name": "High risk, sanctions",
        "vendor": "Nexus Global Holdings",
        "expect_score": 72,
        "expect_completeness": "full",
        "expect_red_flags_empty": False,
        "expect_path": "Human Review → Reject",
        "validates": "Override audit trail"
    },
    {
        "id": 3,
        "name": "API total failure",
        "vendor": "ErrorTrigger Inc.",
        "expect_status": 503,
        "expect_path": "Retry → Human Alert",
        "validates": "Graceful failure (Art. 15)"
    },
    {
        "id": 4,
        "name": "Partial data state",
        "vendor": "PartialData Corp",
        "expect_completeness": "partial",
        "expect_path": "Human Review w/ warning",
        "validates": "SHIELDA flow control"
    },
    {
        "id": 5,
        "name": "Low risk score (boundary)",
        "vendor": "Borderline Safe Inc",
        "expect_score": 25,
        "expect_completeness": "full",
        "expect_red_flags_empty": True,
        "expect_path": "Auto-Approve",
        "validates": "Algorithmic conformity test bed"
    },
    {
        "id": 6,
        "name": "Timer expiration (simulated)",
        "vendor": "__TIMER_TEST__",
        "expect_path": "Escalation webhook sent",
        "validates": "SLA Procurement adherence",
        "skip_api": True  # Timer test is BPMN-side, not API-side
    },
    {
        "id": 7,
        "name": "Conflicting data",
        "vendor": "Conflict Industries",
        "expect_conflicting": True,
        "expect_path": "Human Review",
        "validates": "Ambiguity handling"
    },
    {
        "id": 8,
        "name": "Hallucinated vendor",
        "vendor": "asdfghjkl corp",
        "expect_completeness": "none",
        "expect_new_entity": True,
        "expect_path": "Human Review: Not Found",
        "validates": "Adversarial robustness"
    },
    {
        "id": 9,
        "name": "Predictive multiplicity",
        "vendor": "Uncertain Ventures",
        "expect_multiplicity": True,
        "expect_path": "Human Review",
        "validates": "Mathematical uncertainty"
    },
    {
        "id": 10,
        "name": "DMN priority override",
        "vendor": "Sneaky Risk Ltd",
        "expect_score": 25,
        "expect_red_flags_empty": False,
        "expect_path": "Escalate (Priority 1)",
        "validates": "DMN Hit Policy"
    },
    {
        "id": 11,
        "name": "Primary LLM provider outage",
        "vendor": "providerfallback test",
        "expect_status": 500,
        "expect_path": "Fallback → Normal evaluation",
        "validates": "Art. 15 robustness + provider fallback"
    },
]


# ============================================================
# Test Runner
# ============================================================

def run_tests():
    passed = 0
    failed = 0
    skipped = 0
    results = []

    print(f"{'='*70}")
    print(f"  THIRD-PARTY RISK GATE — AUTOMATED TEST MATRIX (11 Cases)")
    print(f"{'='*70}\n")

    for test in TESTS:
        test_id = test["id"]
        name = test["name"]
        vendor = test["vendor"]

        # Skip non-API tests
        if test.get("skip_api"):
            print(f"  ⏭️  TEST {test_id}: {name} — SKIPPED (BPMN-side test)")
            skipped += 1
            results.append({"id": test_id, "status": "SKIPPED"})
            continue

        try:
            response = httpx.get(
                f"{MOCK_BASE}/assess_vendor/{vendor}",
                timeout=10.0
            )

            # Tests that expect HTTP errors
            if "expect_status" in test:
                if response.status_code == test["expect_status"]:
                    print(f"  ✅ TEST {test_id}: {name} — PASSED (HTTP {response.status_code})")
                    passed += 1
                    results.append({"id": test_id, "status": "PASSED"})
                else:
                    print(f"  ❌ TEST {test_id}: {name} — FAILED (Expected HTTP {test['expect_status']}, got {response.status_code})")
                    failed += 1
                    results.append({"id": test_id, "status": "FAILED", "reason": f"HTTP {response.status_code}"})
                continue

            # Tests that expect successful responses
            response.raise_for_status()
            data = response.json()
            assessment = VendorRiskAssessment(**data)

            # Validate expectations
            errors = []

            if "expect_score" in test and assessment.risk_score != test["expect_score"]:
                errors.append(f"score: expected {test['expect_score']}, got {assessment.risk_score}")

            if "expect_completeness" in test and assessment.data_completeness.value != test["expect_completeness"]:
                errors.append(f"completeness: expected {test['expect_completeness']}, got {assessment.data_completeness.value}")

            if "expect_red_flags_empty" in test:
                is_empty = len(assessment.red_flags) == 0
                if is_empty != test["expect_red_flags_empty"]:
                    errors.append(f"red_flags empty: expected {test['expect_red_flags_empty']}, got {is_empty}")

            if "expect_conflicting" in test and assessment.conflicting_data != test["expect_conflicting"]:
                errors.append(f"conflicting: expected {test['expect_conflicting']}, got {assessment.conflicting_data}")

            if "expect_new_entity" in test and assessment.new_entity_no_history != test["expect_new_entity"]:
                errors.append(f"new_entity: expected {test['expect_new_entity']}, got {assessment.new_entity_no_history}")

            if "expect_multiplicity" in test and assessment.predictive_multiplicity_flag != test["expect_multiplicity"]:
                errors.append(f"multiplicity: expected {test['expect_multiplicity']}, got {assessment.predictive_multiplicity_flag}")

            if errors:
                print(f"  ❌ TEST {test_id}: {name} — FAILED")
                for err in errors:
                    print(f"      → {err}")
                failed += 1
                results.append({"id": test_id, "status": "FAILED", "errors": errors})
            else:
                print(f"  ✅ TEST {test_id}: {name} — PASSED")
                passed += 1
                results.append({"id": test_id, "status": "PASSED"})

        except Exception as e:
            print(f"  ❌ TEST {test_id}: {name} — ERROR: {e}")
            failed += 1
            results.append({"id": test_id, "status": "ERROR", "reason": str(e)})

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {passed} PASSED | {failed} FAILED | {skipped} SKIPPED")
    print(f"{'='*70}\n")

    # Exit code for CI/CD
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    run_tests()
