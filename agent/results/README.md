# Test Results

## Pipeline Execution — 2025-07-12

```
======================================================================
  FULL PIPELINE TEST — 11 Cases (End-to-End)
======================================================================

  ✅ TEST 1: Happy path, low risk — PASSED (route: auto_approve)
  ✅ TEST 2: High risk, sanctions — PASSED (route: escalate)
  ✅ TEST 3: API total failure — PASSED (Error handled: Primary LLM provider error: 503)
  ✅ TEST 4: Partial data state — PASSED (route: human_review)
  ✅ TEST 5: Low risk score (boundary) — PASSED (route: auto_approve)
  ⏭️  TEST 6: Timer expiration — SKIPPED (BPMN-side)
  ✅ TEST 7: Conflicting data — PASSED (route: human_review)
  ✅ TEST 8: Hallucinated vendor — PASSED (route: human_review)
  ✅ TEST 9: Predictive multiplicity — PASSED (route: human_review)
  ✅ TEST 10: DMN priority override — PASSED (route: escalate)
  ✅ TEST 11: Primary LLM provider outage — PASSED (Error handled: ...)

──────────────────────────────────────────────────────────────────────
  AUDIT TRAIL: 8 entries written
  ✅ All 8 audit entries valid and immutable

======================================================================
  SUMMARY: 10 PASSED | 0 FAILED | 1 SKIPPED
======================================================================
```

## Sample Audit Trail Entry

```json
{
  "timestamp": "2025-07-12T14:32:07.451234+00:00",
  "vendor_name": "Nexus Global Holdings",
  "vendor_headquarters_country": "Panama",
  "risk_score": 72,
  "red_flags": ["sanctions_list_match", "negative_news"],
  "data_completeness": "full",
  "predictive_multiplicity_flag": false,
  "conflicting_data": false,
  "ai_recommendation": "escalate",
  "route_taken": "escalate",
  "human_decision": null,
  "human_reviewer": null,
  "override_flag": false,
  "override_justification": null,
  "agent_1_model": "gpt-4o-2024-08-06",
  "agent_2_model": "claude-3-5-sonnet-20241022"
}
```

## Routing Distribution

| Route | Count | Vendors |
|---|---|---|
| Auto-Approve | 2 | ClearPath Logistics, Borderline Safe Inc |
| Human Review | 4 | PartialData Corp, Conflict Industries, asdfghjkl corp, Uncertain Ventures |
| Escalate | 2 | Nexus Global Holdings, Sneaky Risk Ltd |
| Error (handled) | 2 | ErrorTrigger Inc., providerfallback test |
