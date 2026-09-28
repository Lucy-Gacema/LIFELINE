import { apiFetch } from "./client.js";

export const createSale = (data) => apiFetch("/api/v1/sales/", { method: "POST", body: JSON.stringify(data) });
export const listSales = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return apiFetch(`/api/v1/sales/${qs ? `?${qs}` : ""}`);
};
export const getSale = (id) => apiFetch(`/api/v1/sales/${id}`);
export const voidSale = (id, reason) => apiFetch(`/api/v1/sales/${id}/void?reason=${encodeURIComponent(reason)}`, { method: "POST" });
export const createRefund = (data) => apiFetch("/api/v1/sales/refunds", { method: "POST", body: JSON.stringify(data) });
