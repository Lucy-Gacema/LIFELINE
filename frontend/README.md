# LIFELINE POS — Frontend

Offline-first React + Vite app. Works entirely from a cached product catalog
and a local sync queue when there's no internet connection.

## Setup

```bash
npm install
cp .env.example .env      # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

## Project layout

```
src/
  api/            Thin fetch wrappers per backend domain (client.js has the shared logic)
  db/
    index.js        IndexedDB wrapper (products cache, sync queue, cart draft, held sales)
    sync.js           The sync engine: pushes queued ops when online, retries on failure
  hooks/
    useAuth.jsx        Auth context (token, current user, permission checks)
    useOnlineStatus.js  Subscribes to sync status (online/offline/syncing/error)
  components/       Shared UI (AppShell/nav, ProductGrid, CartPanel, PaymentModal, ...)
  pages/            One file per route
```

## How offline mode works

1. Products are fetched from the API on load and cached into IndexedDB
   (`cacheProducts`). If the initial fetch fails, the Sell screen falls back
   to the cached copy so it still works with zero connectivity.
2. When a sale is completed, the app first tries the real API call. If that
   fails because we're offline (`ApiError.status === 0`), the sale is instead:
   - written to a local `sync_queue` entry (with a `crypto.randomUUID()`
     idempotency key),
   - saved to `local_sales` so it shows up immediately as a receipt,
   - applied optimistically to the local product-stock cache.
3. `db/sync.js` listens for the browser's `online` event (plus a 30s poll as
   a safety net) and pushes everything in the queue to
   `POST /api/v1/sync/push`. Applied operations are removed from the queue;
   failed ones are left in place and retried next time — nothing is ever
   silently dropped, and the sync badge (top of the nav) reflects the current
   state (`Online` / `Offline` / `Syncing…` / `Sync error`).

## Known scope limits

- No service worker / installable PWA shell is included — the app is
  offline-*functional* (works with no network once loaded) but won't
  currently load from a cold cache with zero connectivity on first visit.
  Adding a Workbox-based service worker to precache the built assets would
  close that gap if you need true installable-PWA behavior.
- Voice input/output uses the browser's built-in Web Speech API
  (`SpeechRecognition` / `speechSynthesis`). Support varies by browser —
  Chrome/Edge on desktop and Android work well; Safari/iOS support is
  inconsistent. Text chat always works as a fallback.
- Purchase orders / GRN, and full receipt-delivery options (SMS/email/thermal
  print), are backend-ready but don't have dedicated frontend screens yet —
  see the root README's "known scope limits" section.

**Note:** `npm install` could not be run in the environment this was built
in (no registry access), so the app was reviewed statically (import
resolution + bracket-balance checked across every file) rather than build-
or runtime-tested. Please run `npm run build` yourself as a first check.
