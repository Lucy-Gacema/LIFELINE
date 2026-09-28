import { useEffect, useState } from "react";
import { onSyncStatusChange } from "../db/sync.js";

export function useSyncStatus() {
  const [status, setStatus] = useState("online");
  useEffect(() => onSyncStatusChange((s) => setStatus(s)), []);
  return status;
}
