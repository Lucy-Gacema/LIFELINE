# LIFELINE POS — Backend

FastAPI + SQLAlchemy backend. Ships with SQLite by default (zero setup,
great for a single shop) and supports Postgres for multi-device cloud sync.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py                  # creates your first Admin user + sample products
uvicorn main:app --reload
```

The API is now at http://localhost:8000, with interactive docs at
http://localhost:8000/docs.

## Configuration

All settings are environment variables (see `.env.example`), loaded in
`lifeline/core/config.py`. Nothing sensitive is hardcoded in source.

Key ones:
- `DATABASE_URL` — defaults to a local SQLite file. Set to a Postgres URL for
  production / multi-device sync.
- `SECRET_KEY` — change this before deploying anywhere real.
- `AI_PROVIDER` / `ANTHROPIC_API_KEY` — set a key to enable full
  natural-language AI Assistant behavior. Set `AI_PROVIDER=none` to force the
  built-in rule-based fallback only.
- `ALLOWED_ORIGINS` — comma-separated frontend origins allowed by CORS.

## Project layout

```
main.py                 App entrypoint, router wiring, CORS, global error handler
database.py              SQLAlchemy engine/session
dependencies.py           Auth dependencies (get_current_user, require_permission)
seed.py                   First-run setup script
lifeline/
  core/
    config.py             Settings (env-driven)
    security.py            Password/PIN hashing, JWT
  models/                  SQLAlchemy ORM models (one file per entity)
  schemas/                 Pydantic request/response schemas
  services/                Business logic — the ONLY place that touches models directly
    sale_service.py         Core checkout logic (idempotent, atomic stock+payment)
    inventory_service.py    Single choke point for every stock mutation
    ai_tools.py              Structured tools the AI is allowed to call
    ai_tool_schemas.py       Anthropic tool-use JSON schemas
    ai_agent.py               Orchestrates the AI conversation + confirmation flow
    report_service.py         All read-only analytics (shared by UI and AI)
  routers/                 Thin FastAPI route handlers — call services, no business logic here
  tests/                    Pytest suite
```

## Design notes worth knowing before you extend this

- **Idempotency is load-bearing.** Every sale carries a client-generated
  `idempotency_key`. `sale_service.create_sale` checks for an existing sale
  with that key before doing anything else, so a retried request (e.g. from
  an offline sync replay) can never create a duplicate transaction or
  double-deduct stock.
- **Inventory only ever changes through `inventory_service.adjust_stock`.**
  Every call writes an `InventoryLogs` row with the previous/new quantity and
  reason. Don't mutate `Product.current_stock` directly anywhere else.
- **Permissions are attached to users, not hardcoded per-role checks
  everywhere.** `User.has_permission(...)` merges role defaults with any
  per-user `custom_permissions` overrides. Both the REST API
  (`dependencies.require_permission`) and the AI tools
  (`ai_tools.TOOL_PERMISSIONS`) use the same mechanism.
- **The AI can only call the same service functions the REST API calls.**
  There is no raw-SQL or free-form database access path for the AI — see
  `ai_tools.py`. Medium/high-risk tools are never auto-executed; the agent
  returns a `ProposedAction` and waits for an explicit confirm call.

## Running tests

```bash
pytest
```

Covers: idempotent sale creation, insufficient-stock blocking, permission
enforcement (a Cashier can't view profit reports), and the AI Assistant's
propose → confirm → execute flow.

**Note:** this environment could not install packages or run the server to
verify at runtime (no network access during generation) — everything was
statically reviewed and compiled (`py_compile`), and the logic was traced by
hand, but please run `pytest` yourself before relying on this in production.
