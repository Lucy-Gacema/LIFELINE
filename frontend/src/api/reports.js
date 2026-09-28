import { apiFetch } from "./client.js";

export const getSalesSummary = (period = "today") => apiFetch(`/api/v1/reports/sales-summary?period=${period}`);
export const getProfitSummary = (period = "today") => apiFetch(`/api/v1/reports/profit-summary?period=${period}`);
export const getTopProducts = (period = "today", by = "quantity") => apiFetch(`/api/v1/reports/top-products?period=${period}&by=${by}`);
export const getBusinessHealth = () => apiFetch("/api/v1/reports/business-health");
export const getSlowMoving = () => apiFetch("/api/v1/reports/slow-moving");
