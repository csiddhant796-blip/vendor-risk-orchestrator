# Third-Party Risk Gate

Adversarial dual-agent vendor due-diligence pipeline with deterministic DMN routing,
human-in-the-loop oversight, and an immutable audit trail — designed against EU AI Act
Articles 6–15.

UiPath AgentHack 2026 · Track 2 (Maestro / BPMN)

---

## Repository layout

```
vendor-risk-orchestrator/
├── agent/        Swarup's Python pipeline (the working intelligence layer)
├── maestro/      UiPath Maestro BPMN process + DMN table (Platform Lead)
├── ui/           Action Center form / cognitive-friction UI reference
├── docs/         Project overview, demo script
├── requirements.txt
└── README.md
```

## The `agent/` directory

This is Swarup's complete, tested Python backend. The files are kept **flat** inside
`agent/` on purpose: the modules import each other as siblings (`from pipeline import ...`,
`from dmn_engine import ...`), so they must live in one directory to run. The flat layout
maps onto the system's logical architecture as follows:

| Architecture layer | File(s) |
|---|---|
| Data contracts | `models.py` |
| Mock data source | `mock_server.py` |
| Agent 1 (GPT-4o, high recall) | `agent1.py`, `agent1_prompt.py` |
| Agent 2 (Claude 3.5 Sonnet, high precision) | `agent2_prompt.py`, `agent2_mock.py` |
| DMN routing gateway (9 rules, PRIORITY) | `dmn_engine.py` |
| Immutable audit trail | `audit_logger.py` |
| Orchestrator (Agent1 → slim → Agent2 → DMN → audit) | `pipeline.py` |
| Tests | `test_matrix.py`, `test_pipeline.py` |
| Live API check | `live_test_opencorporates.py` |

## Running the tests

The test suites require **both** LangChain installed **and** the mock server running.

```bash
cd agent
pip install -r requirements.txt        # installs LangChain etc.
python mock_server.py &                 # start mock API on :8000
python test_matrix.py                   # API-level (10 pass, 1 skip)
python test_pipeline.py                 # end-to-end (10 pass, 1 skip)
```

> Note: the project README states direct mode needs no dependencies, but `agent1.py`
> imports LangChain at module load, so `pip install -r requirements.txt` is required
> even for mock-mode tests. The mock server must also be running first.

See `docs/PROJECT_OVERVIEW.md` for the full architecture, EU AI Act compliance matrix,
and academic foundation.
