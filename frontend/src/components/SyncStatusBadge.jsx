import React from "react";
import { useSyncStatus } from "../hooks/useOnlineStatus.js";

const CONFIG = {
  online: { label: "Online", dot: "bg-brand-500", text: "text-brand-700", bg: "bg-brand-50" },
  offline: { label: "Offline — sales will sync when connection returns", dot: "bg-gray-400", text: "text-gray-700", bg: "bg-gray-100" },
  syncing: { label: "Syncing…", dot: "bg-amber-500 animate-pulse", text: "text-amber-700", bg: "bg-amber-50" },
  sync_error: { label: "Sync error — action needed", dot: "bg-red-500", text: "text-red-700", bg: "bg-red-50" },
};

export default function SyncStatusBadge({ compact = false }) {
  const status = useSyncStatus();
  const cfg = CONFIG[status] || CONFIG.online;
  return (
    <div className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium ${cfg.bg} ${cfg.text}`} role="status">
      <span className={`h-2.5 w-2.5 rounded-full ${cfg.dot}`} aria-hidden="true" />
      {!compact && <span>{cfg.label}</span>}
    </div>
  );
}
