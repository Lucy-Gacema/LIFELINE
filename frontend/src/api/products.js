import { apiFetch } from "./client.js";

export const listProducts = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return apiFetch(`/api/v1/products/${qs ? `?${qs}` : ""}`);
};
export const searchProducts = (q) => apiFetch(`/api/v1/products/search?q=${encodeURIComponent(q)}`);
export const getLowStockProducts = () => apiFetch("/api/v1/products/low-stock");
export const createProduct = (data) => apiFetch("/api/v1/products/", { method: "POST", body: JSON.stringify(data) });
export const updateProduct = (id, data) => apiFetch(`/api/v1/products/${id}`, { method: "PATCH", body: JSON.stringify(data) });
export const deactivateProduct = (id) => apiFetch(`/api/v1/products/${id}`, { method: "DELETE" });
export const listCategories = () => apiFetch("/api/v1/products/categories/");
export const createCategory = (data) => apiFetch("/api/v1/products/categories/", { method: "POST", body: JSON.stringify(data) });
