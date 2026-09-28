import React, { useEffect, useState } from "react";
import * as productsApi from "../api/products.js";
import Loading from "../components/Loading.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

export default function Inventory() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    productsApi.listProducts().then(setProducts).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  const filtered = products.filter((p) => filter === "all" || p.stock_status === filter);

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      <h1 className="text-2xl font-bold mb-4">Inventory</h1>
      <ErrorBanner message={error} />
      <div className="flex gap-2 mb-4 overflow-x-auto">
        {["all", "healthy", "low", "critical", "out_of_stock"].map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap ${filter === f ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            {f.replace("_", " ")}
          </button>
        ))}
      </div>
      {loading ? <Loading /> : (
        <div className="card overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-sm text-gray-500">
              <tr><th className="px-4 py-3">Product</th><th className="px-4 py-3">Stock</th><th className="px-4 py-3">Minimum</th><th className="px-4 py-3">Status</th></tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map((p) => (
                <tr key={p.product_id}>
                  <td className="px-4 py-3 font-medium">{p.product_name}</td>
                  <td className="px-4 py-3">{p.current_stock} {p.unit}</td>
                  <td className="px-4 py-3 text-gray-500">{p.minimum_stock}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      p.stock_status === "out_of_stock" ? "bg-red-100 text-red-700" :
                      p.stock_status === "critical" ? "bg-red-50 text-red-600" :
                      p.stock_status === "low" ? "bg-amber-50 text-amber-700" : "bg-brand-50 text-brand-700"
                    }`}>{p.stock_status.replace("_", " ")}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
