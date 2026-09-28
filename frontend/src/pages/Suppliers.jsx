import React, { useEffect, useState } from "react";
import { apiFetch } from "../api/client.js";
import Loading from "../components/Loading.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [reorderList, setReorderList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "" });

  const load = () => {
    Promise.all([apiFetch("/api/v1/suppliers/"), apiFetch("/api/v1/suppliers/reorder-planner/list")])
      .then(([s, r]) => { setSuppliers(s); setReorderList(r); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await apiFetch("/api/v1/suppliers/", { method: "POST", body: JSON.stringify(form) });
      setForm({ name: "", phone: "" });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-8">
      <div>
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Suppliers</h1>
          <button className="btn-primary" onClick={() => setShowForm(true)}>+ Add supplier</button>
        </div>
        <ErrorBanner message={error} onDismiss={() => setError("")} />
        {suppliers.length === 0 ? (
          <EmptyState icon="🚚" title="No suppliers yet" />
        ) : (
          <ul className="card divide-y">
            {suppliers.map((s) => (
              <li key={s.supplier_id} className="px-4 py-3 flex justify-between">
                <div>
                  <p className="font-semibold">{s.name}</p>
                  <p className="text-sm text-gray-500">{s.phone || "—"}</p>
                </div>
                {Number(s.amount_owed) > 0 && <p className="text-amber-600 font-semibold">Owe KSh {Number(s.amount_owed).toFixed(0)}</p>}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h2 className="text-xl font-bold mb-3">Reorder planner</h2>
        {reorderList.length === 0 ? (
          <p className="text-gray-400 text-sm">Nothing needs reordering right now.</p>
        ) : (
          <div className="card overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-gray-50 text-sm text-gray-500">
                <tr><th className="px-4 py-3">Product</th><th className="px-4 py-3">Current</th><th className="px-4 py-3">Minimum</th><th className="px-4 py-3">Suggested reorder</th></tr>
              </thead>
              <tbody className="divide-y">
                {reorderList.map((r) => (
                  <tr key={r.product_id}>
                    <td className="px-4 py-3 font-medium">{r.product_name}</td>
                    <td className="px-4 py-3">{r.current_stock}</td>
                    <td className="px-4 py-3 text-gray-500">{r.minimum_stock}</td>
                    <td className="px-4 py-3 font-semibold text-brand-700">{r.suggested_reorder_quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form onSubmit={handleSubmit} className="card w-full max-w-sm p-6">
            <h2 className="text-xl font-bold mb-4">Add supplier</h2>
            <div className="space-y-3">
              <input required autoFocus className="input" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              <input className="input" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div className="flex gap-3 mt-6">
              <button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary flex-1">Save</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
