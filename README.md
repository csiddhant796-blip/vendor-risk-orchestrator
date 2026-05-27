# Vendor Risk Orchestrator
### UiPath AgentHack 2026 — Track 2: Maestro BPMN

> AI-powered vendor due diligence platform that orchestrates dual LLM agents through a BPMN workflow with DMN-driven routing and human-in-the-loop escalation.

---

## What It Does

Automates vendor onboarding risk assessment by:
1. **Agent 1 (Investigator)** — gathers evidence from OpenCorporates + NewsAPI, scores vendor risk (0–100)
2. **DMN Table** — routes based on score: Auto-Approve / Human Review / Auto-Reject
3. **Agent 2 (Auditor)** — independently audits Agent 1's reasoning for human review cases
4. **UiPath Action Center** — presents structured brief to compliance officer
5. **Audit Logger** — writes every decision to Google Sheets with full reasoning trail

---

## Architecture

```
Vendor Input → Agent 1 (LangChain ReAct + GPT-4o)
                     ↓
              DMN Risk Table
           ┌──────┼──────────┐
      Auto-Approve  Human   Auto-Reject
                   Review
                     ↓
              Agent 2 (Auditor)
              Claude 3.5 Sonnet
                     ↓
           UiPath Action Center
                     ↓
              Audit Logger (Google Sheets)
```

See [`docs/architecture.md`](docs/architecture.md) for full detail.

---

## Integrations

| Layer | Technology |
|---|---|
| Orchestration | UiPath Maestro (BPMN) |
| Decision Logic | UiPath DMN (PRIORITY hit policy) |
| Agent 1 | LangChain ReAct + GPT-4o |
| Agent 2 | Claude 3.5 Sonnet (Anthropic) |
| Data Sources | OpenCorporates API, NewsAPI |
| Human Handoff | UiPath Action Center |
| Audit Trail | Google Sheets API |
| Notifications | Slack Webhook |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/csiddhant796-blip/vendor-risk-orchestrator
cd vendor-risk-orchestrator

# 2. Install dependencies
pip install -r agent/requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Run mock server (Terminal 1)
python agent/mock_server.py

# 5. Run Agent 1 (Terminal 2)
python agent/agent1.py
```

---

## Repo Structure

```
vendor-risk-orchestrator/
├── agent/              # Python — Agent 1, Agent 2, mock server
├── maestro/            # UiPath BPMN exports
├── docs/               # Architecture, AI coding journal
├── tests/              # Test matrix — all 11 vendor cases
└── README.md
```

---

## Team

| Person | Role |
|---|---|
| Siddhant C (Person A) | Platform Lead — UiPath Maestro, BPMN, DMN |
| Swarup (Person B) | Intelligence Lead — LangChain Agents, Python |

---

## Submission

- **Hackathon:** UiPath AgentHack 2026
- **Track:** Track 2 — Intelligent Document & Data Workflows (Maestro BPMN)
- **Devpost:** *(link to be added)*
- **Demo Video:** *(link to be added)*

---

## License

MIT — see [LICENSE](LICENSE)
