# Agent Code

This folder contains all Python agent code.

## Files (Swarup adds these)
- `mock_server.py` — FastAPI mock vendor data server (8 seed vendors)
- `models.py` — Pydantic data models
- `agent1.py` — LangChain ReAct Agent 1 (Investigator)
- `agent1_prompt.py` — Agent 1 system prompt
- `agent2_prompt.py` — Agent 2 system prompt (Auditor) — Week 2
- `audit_logger.py` — Google Sheets audit trail writer — Week 2
- `requirements.txt` — Python dependencies

## Running Locally

```bash
# Terminal 1
python mock_server.py

# Terminal 2
python agent1.py
```

Expected output for all 8 seed vendors documented in `docs/architecture.md`.
