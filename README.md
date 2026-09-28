# LIFELINE POS

A simple, offline-first point-of-sale and small-business management system
for independent shop owners — built to feel like "a simple shop assistant
that also happens to be a POS," not an enterprise ERP.

This archive contains a complete backend (FastAPI + SQLAlchemy) and frontend
(React + Vite, offline-first with IndexedDB) implementing the core product:
fast tap-to-sell checkout, inventory, customers, suppliers, cash/shifts,
expenses, reports, and an AI Business Assistant (text + voice) that can
record sales and answer business questions in plain language.

## What's inside

```
lifeline_pos/
├── backend/        FastAPI backend (see backend/README.md)
└── frontend/       React + Vite frontend (see frontend/README.md)
```

## Fastest way to try it

**1. Backend**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # defaults to a local SQLite file — no DB setup needed
python seed.py                # creates your first Admin user + sample products
uvicorn main:app --reload
```

**2. Frontend** (new terminal)
```bash
cd frontend
npm install
cp .env.example .env          # points at http://localhost:8000 by default
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173), log in with the
admin credentials `seed.py` printed, open your till, and try a sale.

## Design principles this build follows

- **The Sell screen is the product.** Everything else supports it.
- **The AI never silently does anything financially significant.** Sales,
  refunds, price changes, and inventory adjustments always get a plain-language
  confirmation card before they execute — see `backend/lifeline/services/ai_agent.py`.
- **Offline is a first-class state, not an error state.** The frontend caches
  products in IndexedDB, queues sales locally with a client-generated
  idempotency key, and syncs them once connectivity returns — duplicates are
  structurally impossible because the server dedupes on that same key.
- **Every financial/inventory mutation is logged.** See `AuditLog` and
  `InventoryLogs` — nothing changes stock or money without a traceable reason.
- **Permissions are granular and the AI inherits them.** A cashier asking the
  assistant for a profit report gets the same "you don't have permission"
  response the REST API would give.

## Known scope limits (read before deploying)

This is a complete, working build of the core product — but a few things
were deliberately kept simple given the size of the original spec, and you
should treat them as a v1 rather than a finished enterprise product:

- **AI Assistant**: full natural-language understanding (ambiguous product
  names, multi-item sentences, business questions) requires an Anthropic API
  key in `backend/.env` (`ANTHROPIC_API_KEY`). Without one, a lightweight
  rule-based fallback still handles basic "I sold 2 milk and 1 bread" style
  sales entry and a few common questions, but it's not a substitute for the
  real thing.
- **Purchase orders / GRN**: the data model and API are complete
  (`lifeline/routers/suppliers.py`, `goods_received.py`), but the frontend
  only exposes supplier records and the reorder planner, not a full PO/GRN
  UI — build it out from the existing endpoints as needed.
- **Receipts**: the frontend shows an on-screen + printable receipt; thermal
  printer, SMS and email receipt delivery are not wired up (hardware
  integration was explicitly out of scope for this build per your request).
- **Multi-device conflict resolution** is last-write-wins at the field level
  (via normal DB updates) plus idempotent sale/inventory operations. There's
  no CRDT-style merge for two offline devices editing the *same* product at
  the *same* time — for a single-shop, mostly-one-device use case this is a
  reasonable tradeoff, but call it out if you scale to many concurrent
  devices.
- **Tests**: `backend/lifeline/tests/` has a focused suite covering the
  riskiest paths (idempotent sales, insufficient-stock blocking, permission
  enforcement, the AI confirmation flow) rather than exhaustive coverage of
  every endpoint. Run it with `pytest` from `backend/`.

## Where to look for each spec area

| Area | Backend | Frontend |
|---|---|---|
| Core sell flow | `routers/sales.py`, `services/sale_service.py` | `pages/Sell.jsx` |
| Offline sync | `routers/sync.py` | `db/index.js`, `db/sync.js` |
| AI Assistant | `services/ai_agent.py`, `services/ai_tools.py` | `pages/Assistant.jsx` |
| Permissions | `models/user.py`, `dependencies.py` | `hooks/useAuth.jsx` |
| Inventory | `services/inventory_service.py` | `pages/Inventory.jsx` |
| Shifts / cash drawer | `services/cash_service.py` | `components/ShiftGate.jsx`, `pages/Settings.jsx` |
| Reports / business health | `services/report_service.py` | `pages/Reports.jsx`, `pages/Dashboard.jsx` |
