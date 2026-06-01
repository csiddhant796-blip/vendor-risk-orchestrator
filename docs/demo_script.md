# Demo Script — Third-Party Risk Gate

## Total Time: 3 minutes

---

### Section 1: The Problem (30 seconds)

"Enterprise procurement teams evaluate 500+ vendors per month. Each manual assessment takes 30-45 days and costs $150-300 in analyst time. That's $75,000 to $150,000 per month. And despite all that effort, human reviewers rubber-stamp AI recommendations 19-27% of the time due to algorithmic conformity."

### Section 2: The Architecture (45 seconds)

Show the architecture diagram from README.md.

"We built a dual-agent adversarial pipeline. Agent 1, running on GPT-4o, gathers wide-angle intelligence with high recall. Agent 2, running on Claude 3.5 Sonnet, independently verifies every red flag with high precision. They use different providers to prevent shared bias reinforcement.

Between them, a slimming function strips all reasoning and narrative — Agent 2 receives only bare assertions. This prevents anchoring bias.

A DMN gateway with PRIORITY hit policy makes the routing decision. Red flags always escalate, regardless of score. Auto-approve only fires when everything is clean and the score is below 30."

### Section 3: Live Demo (90 seconds)

**Terminal 1:** `python mock_server.py`
**Terminal 2:** `python pipeline.py`

Walk through 3 key scenarios:

1. **"ClearPath Logistics"** → Score 18, Auto-Approve
   "Clean vendor, full data, no flags. System approves instantly."

2. **"Nexus Global Holdings"** → Score 72, Escalate
   "Sanctions match detected. Agent 2 independently verifies it against the OFAC database. DMN Priority 1 fires — escalate, regardless of any other factor."

3. **"asdfghjkl corp"** → New Entity, Human Review
   "No data found anywhere. The adversarial robustness check flips `new_entity_no_history`. DMN routes to human review with a warning."

**Point to the audit trail:**
"Every decision is logged immutably — timestamp, score, route, models used, headquarters country for bias tracking. Records cannot be modified or deleted."

### Section 4: Compliance & ROI (15 seconds)

"The system maps directly to EU AI Act Articles 6 through 15. Each feature has a compliance matrix entry with evidence for auditors.

And the ROI: from $150,000 per month to $17.50. A 4,000x cost reduction."

---

## Q&A Prep: Top 5 Questions Judges Will Ask

### Q1: "Why not use a single model?"
"Single-model debate creates shared bias reinforcement — both agents share the same training data and architectural biases. Our heterogeneous approach forces orthogonal problem-solving. This is supported by arXiv:2604.02923."

### Q2: "How do you prevent the human from just rubber-stamping?"
"Algorithmic conformity research shows humans adopt erroneous AI advice 19-27% of the time. Our UI implements scaffolded cognitive friction — mandatory justification dropdowns and 50-character minimum text. You cannot click a single 'Approve' button."

### Q3: "What happens when the LLM provider goes down?"
"GPT-4o timeouts trigger automatic fallback to Claude 3.5 Sonnet. If both fail, the BPMN Error Boundary Event catches it and routes to a human alert. This satisfies Article 15 robustness requirements."

### Q4: "How is this different from OneTrust or SecurityScorecard?"
"OneTrust manages manual questionnaires. SecurityScorecard provides external cyber ratings. Neither executes adversarial AI verification bound by a BPMN engine with immutable audit trails mapped to EU AI Act articles."

### Q5: "What about vendors not in any database?"
"The adversarial robustness check detects when zero sources return data. It flips `new_entity_no_history`, which triggers DMN Priority 3 — always routes to human review. The system never auto-approves an unknown entity."
