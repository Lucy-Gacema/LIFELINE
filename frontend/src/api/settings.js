import { apiFetch } from "./client.js";

export const getSettings = () => apiFetch("/api/v1/settings/");
export const updateSettings = (data) => apiFetch("/api/v1/settings/", { method: "PATCH", body: JSON.stringify(data) });
