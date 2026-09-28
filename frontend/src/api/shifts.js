import { apiFetch, ApiError } from "./client.js";

export async function getCurrentShift() {
  try {
    return await apiFetch("/api/v1/shifts/current");
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
export const openShift = (openingCash) => apiFetch("/api/v1/shifts/open", { method: "POST", body: JSON.stringify({ opening_cash: openingCash }) });
export const closeShift = (shiftId, data) => apiFetch(`/api/v1/shifts/${shiftId}/close`, { method: "POST", body: JSON.stringify(data) });
export const getExpectedCash = (shiftId) => apiFetch(`/api/v1/shifts/${shiftId}/expected-cash`);
