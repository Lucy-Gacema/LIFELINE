
import { getQueuedOperations, removeQueuedOperation } from "./index.js";
import { apiFetch } from "../api/client.js";

export const SYNC_STATUS = {
  ONLINE: "online",
  OFFLINE: "offline",
  SYNCING: "syncing",
  SYNC_ERROR: "sync_error",
};

let listeners = [];
let currentStatus = navigator.onLine ? SYNC_STATUS.ONLINE : SYNC_STATUS.OFFLINE;
let pendingCount = 0;

export function onSyncStatusChange(listener) {
  listeners.push(listener);
  listener(currentStatus, pendingCount);
  return () => {
    listeners = listeners.filter((l) => l !== listener);
  };
}

function setStatus(status) {
  currentStatus = status;
  listeners.forEach((l) => l(currentStatus, pendingCount));
}

async function refreshPendingCount() {
  const ops = await getQueuedOperations();
  pendingCount = ops.length;
}

export async function syncNow() {
  if (!navigator.onLine) {
    setStatus(SYNC_STATUS.OFFLINE);
    return;
  }
  const ops = await getQueuedOperations();
  await refreshPendingCount();
  if (ops.length === 0) {
    setStatus(SYNC_STATUS.ONLINE);
    return;
  }

  setStatus(SYNC_STATUS.SYNCING);
  try {
    const response = await apiFetch("/api/v1/sync/push", {
      method: "POST",
      body: JSON.stringify({ operations: ops }),
    });
    for (const result of response.results) {
      if (result.status === "applied" || result.status === "already_applied") {
        await removeQueuedOperation(result.idempotency_key);
      }
     
    }
    await refreshPendingCount();
    setStatus(pendingCount > 0 ? SYNC_STATUS.SYNC_ERROR : SYNC_STATUS.ONLINE);
  } catch (err) {
    console.error("Sync failed:", err);
    setStatus(SYNC_STATUS.SYNC_ERROR);
  }
}

export function initSyncEngine() {
  window.addEventListener("online", () => {
    setStatus(SYNC_STATUS.ONLINE);
    syncNow();
  });
  window.addEventListener("offline", () => setStatus(SYNC_STATUS.OFFLINE));

  refreshPendingCount().then(() => {
    setStatus(navigator.onLine ? SYNC_STATUS.ONLINE : SYNC_STATUS.OFFLINE);
    if (navigator.onLine) syncNow();
  });

  
  setInterval(() => {
    if (navigator.onLine) syncNow();
  }, 30000);
}
