import { apiFetch } from "./client.js";

export const listCustomers = (search = "") => apiFetch(`/api/v1/customers/?search=${encodeURIComponent(search)}`);
export const createCustomer = (data) => apiFetch("/api/v1/customers/", { method: "POST", body: JSON.stringify(data) });
export const getCustomer = (id) => apiFetch(`/api/v1/customers/${id}`);
