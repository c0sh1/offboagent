# Offboarding Security Agent

An AI-driven agent that automates secure offboarding of employees and
contractors across connected SaaS tools (Slack, GitHub, AWS IAM, and
others), maintaining a real-time identity graph, revoking access by
risk priority, and detecting orphaned access that was never properly
revoked.

## The problem

When someone leaves a company, access revocation across 8-15+ SaaS
tools rarely happens on time or consistently. Small/mid-size companies
(10-200 employees) typically lack a dedicated IT/security team and a
$5.2B enterprise IAM market (Okta, JumpCloud) that doesn't fit their
budget or integration capacity. The result: data breaches, unauthorized
access, and IP theft risk that persist for weeks or months after
someone's departure.

## How it works

1. **Identity graph** (`app/models/`): tracks every `Person`
   (employee/contractor), every connected `System`, and the
   `AccessGrant` edges between them (role, risk level, status).
2. **Connectors** (`app/connectors/`): one adapter per SaaS tool,
   behind a common interface (`BaseConnector`). Adding a new system
   means adding one file, no changes elsewhere.
3. **Offboarding service** (`app/services/offboarding_service.py`):
   deterministic, rule-based revocation ordered by risk (critical
   access revoked first), with a full audit trail per action.
4. **Agent** (`app/agent/`): a Claude-powered agent using tool use,
   scoped to a single well-defined task (revoke this person's access
   and report on it) rather than open-ended autonomy.
5. **Orphaned access detection**
   (`app/services/orphan_detection_service.py`): periodically
   cross-checks what each system reports as active against the
   identity graph, flagging access that should have been revoked but
   wasn't.

## Tech stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (MVP) — swappable for Postgres via `DATABASE_URL`
- **AI agent**: Claude (Anthropic API), tool use
- **Config**: pydantic-settings (typed, `.env`-based)

## Project structure

```
app/
├── models/       # Identity graph (Person, System, AccessGrant, audit trail)
├── connectors/   # Adapter pattern: one file per SaaS integration
├── services/     # Business logic (offboarding orchestration, orphan detection)
├── agent/        # Claude tool-use agent
├── api/          # FastAPI routers and Pydantic schemas
└── main.py       # App entry point

scripts/          # End-to-end test scripts (no test framework yet - MVP stage)
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # then fill in your own LLM_API_KEY
python -m scripts.init_db     # creates tables + seeds sample data
```

## Running

```bash
uvicorn app.main:app --reload
```

Interactive API docs: `http://127.0.0.1:8000/docs`

## Key endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/persons` | List all persons |
| GET | `/persons/{id}` | Full identity graph for one person |
| POST | `/offboarding` | Initiate + execute offboarding |
| GET | `/offboarding/{event_id}` | Offboarding status + audit log |
| GET | `/security/orphaned-access` | Cross-check for orphaned access |

## Status

MVP stage. Current connectors (Slack, GitHub, AWS IAM) are mocked to
validate the architecture end-to-end without requiring live
credentials. Real OAuth-based integrations, a frontend, and deployment
are planned next steps.

## License

Not yet decided — private/personal project in development.