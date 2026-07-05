# Offboarding Security Agent

An AI-driven agent that automates secure offboarding of employees and
contractors across connected SaaS tools (Slack, GitHub, AWS IAM, and
others), maintaining a real-time identity graph, revoking access by
risk priority, detecting orphaned access that was never properly
revoked, and exposing all of it through a web dashboard.

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
   `AccessGrant` edges between them (role, risk level, status,
   external account ID).
2. **Connectors** (`app/connectors/`): one adapter per SaaS tool,
   behind a common interface (`BaseConnector`). GitHub and AWS IAM
   have real, live integrations (real revocation via API/boto3);
   Slack, Google Workspace, Microsoft 365, Linear, 1Password, and
   Okta are currently mocked, with the real integration path
   documented in each file. Real connectors fall back to their mock
   automatically when credentials aren't configured.
3. **Offboarding service** (`app/services/offboarding_service.py`):
   deterministic, rule-based revocation ordered by risk (critical
   access revoked first), with a full audit trail per action, and
   graceful handling of partial failures (`completed_with_errors`).
4. **Agent** (`app/agent/`): a Claude-powered agent using tool use,
   scoped to a single well-defined task (revoke this person's access
   and report on it) rather than open-ended autonomy.
5. **Orphaned access detection**
   (`app/services/orphan_detection_service.py`): cross-checks what
   each system reports as active against the identity graph, flagging
   access that should have been revoked but wasn't - the exact
   scenario that motivated this project. Known service accounts (the
   credentials the connectors use themselves) are excluded via
   `SERVICE_ACCOUNT_EMAILS` to avoid false-positive noise.
6. **Web dashboard** (`frontend/`): a React app for managing the
   whole lifecycle without touching the API directly - creating
   people, assigning access, triggering offboarding, reviewing
   history, and monitoring risk signals.

## Tech stack

**Backend**
- Python, FastAPI, SQLAlchemy
- SQLite (MVP) — swappable for Postgres via `DATABASE_URL`
- Claude (Anthropic API), tool use, for the agent layer
- boto3 (AWS IAM), httpx (GitHub REST API)
- pydantic-settings (typed, `.env`-based config)

**Frontend**
- React + Vite
- No UI framework — hand-built design system (dark "security console"
  palette, Space Grotesk / Inter / IBM Plex Mono typography)
- Plain `fetch`-based API client, no state management library needed
  at this scale

## Project structure

app/
├── models/       # Identity graph (Person, System, AccessGrant, audit trail)
├── connectors/   # Adapter pattern: one file per SaaS integration (real + mock)
├── services/     # Business logic (offboarding orchestration, orphan detection)
├── agent/        # Claude tool-use agent
├── api/          # FastAPI routers and Pydantic schemas
└── main.py       # App entry point
frontend/
└── src/
├── api/      # Centralized API client
└── pages/    # Dashboard, Persons, PersonDetail, PersonCreate,
# OffboardingHistory, OrphanedAccessPanel
scripts/          # End-to-end test/demo scripts (no test framework yet - MVP stage)

## Setup

Backend:
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # then fill in your own credentials
python -m scripts.init_db     # creates tables + seeds sample data (8 systems)
```

Frontend:
```bash
cd frontend
npm install
```

## Running

Two servers, in separate terminals:
```bash
uvicorn app.main:app --reload      # backend, http://127.0.0.1:8000
cd frontend && npm run dev         # frontend, http://localhost:5173
```

Interactive API docs: `http://127.0.0.1:8000/docs`

### Optional: enabling real connectors

Real connectors activate automatically once their credentials are
present in `.env` - no code changes needed:

| Connector | Required `.env` variables |
|---|---|
| GitHub | `GITHUB_ACCESS_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO` |
| AWS IAM | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |
| Agent (Claude) | `LLM_API_KEY`, `LLM_MODEL` |

Optionally set `SERVICE_ACCOUNT_EMAILS` (comma-separated) to exclude
your own connector credentials from orphaned-access findings.

## Key endpoints

| Method | Path | Description |
|---|---|---|
| GET/POST | `/persons` | List / create persons |
| GET | `/persons/{id}` | Full identity graph for one person |
| POST | `/persons/{id}/access-grants` | Assign an access grant to a person |
| GET | `/systems` | List connected systems |
| POST | `/offboarding` | Initiate + execute offboarding |
| GET | `/offboarding` | Full offboarding history |
| GET | `/offboarding/{event_id}` | Single event status + audit log |
| GET | `/security/orphaned-access` | Cross-check for orphaned access |
| GET | `/dashboard/stats` | Aggregated counts for the dashboard |

## Status

MVP stage, with a working full-stack demo: identity graph, 2 real
connectors (GitHub, AWS IAM) plus 6 mocked ones, deterministic
offboarding with risk prioritization, a Claude tool-use agent
(implemented, pending a live test run), orphaned access detection, and
a complete React dashboard covering the whole person lifecycle.

Next steps under consideration: real connectors for Google Workspace
and Microsoft 365 (both support full API-based revocation, unlike
Slack/1Password/Notion which gate it behind Enterprise plans),
authentication, multi-tenancy, and deployment.

## License

Not yet decided — private/personal project in development.