import { apiFetch } from "./client.js";

export const listHeldSales = () => apiFetch("/api/v1/held-sales/");
export const holdSale = (label, cart) => apiFetch(`/api/v1/held-sales/?label=${encodeURIComponent(label || "")}`, { method: "POST", body: JSON.stringify(cart) });
export const resumeSale = (id) => apiFetch(`/api/v1/held-sales/${id}/resume`, { method: "POST" });
