# Architecture

> Full architecture document will be added here.

## System Overview

The system uses a dual-agent pattern orchestrated by UiPath Maestro BPMN:

1. **Agent 1 — Investigator** (LangChain ReAct, GPT-4o)
   - Queries OpenCorporates and NewsAPI
   - Returns structured JSON: risk score, flags, data completeness

2. **DMN Decision Table** (UiPath Maestro)
   - PRIORITY hit policy
   - 9 rules covering score ranges + flag overrides

3. **Agent 2 — Auditor** (Claude 3.5 Sonnet)
   - Independently reviews Agent 1 output
   - Adversarial — looks for disqualifying flags

4. **UiPath Action Center**
   - Human compliance officer review
   - 48-hour timer boundary escalation

5. **Audit Logger**
   - Every decision written to Google Sheets
   - Fields: vendor, score, path taken, agent reasoning, human override (if any)

## Test Cases

| Vendor | Expected Score | Expected Path |
|---|---|---|
| ClearPath Logistics | 18 | Auto-Approve |
| Nexus Global Holdings | 72 | Auto-Reject (sanctions) |
| ErrorTrigger Inc. | N/A | Exception Handler |
| asdfghjkl corp | N/A | Human Review (new entity) |
| Sneaky Risk Ltd | 25 | Human Review (red flag override) |
| *(6 more TBD)* | | |
