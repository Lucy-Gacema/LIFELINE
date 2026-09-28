import { apiFetch } from "./client.js";


export const sendAssistantMessage = (payload) =>
  apiFetch("/api/v1/assistant/message", { method: "POST", body: JSON.stringify(payload) });

export const getDailyBriefing = () => apiFetch("/api/v1/assistant/daily-briefing");
