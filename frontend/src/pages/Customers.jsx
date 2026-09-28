import React, { useEffect, useState } from "react";
import * as customersApi from "../api/customers.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import Loading from "../components/Loading.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "" });
  const [saving, setSaving] = useState(false);

  const load = (q = "") => {
    setLoading(true);
    customersApi.listCustomers(q).then(setCustomers).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };

  useEffect(() => load(), []);
  useEffect(() => {
    const t = setTimeout(() => load(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await customersApi.createCustomer(form);
      setForm({ name: "", phone: "" });
      setShowForm(false);
      load(search);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 sm:p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Customers</h1>
        <button type="button" className="btn-primary" onClick={() => setShowForm(true)}>+ Add customer</button>
      </div>
      <ErrorBanner message={error} onDismiss={() => setError("")} />
      <input className="input mb-4" placeholder="Find John, or a phone number…" value={search} onChange={(e) => setSearch(e.target.value)} />

      {loading ? <Loading /> : customers.length === 0 ? (
        <EmptyState icon="👥" title="No customers yet" description="Add regulars so you can track credit and repeat purchases." />
      ) : (
        <ul className="card divide-y">
          {customers.map((c) => (
            <li key={c.customer_id} className="px-4 py-3 flex justify-between items-center">
              <div>
                <p className="font-semibold">{c.name}</p>
                <p className="text-sm text-gray-500">{c.phone || "—"}</p>
              </div>
              <div className="text-right text-sm">
                {Number(c.outstanding_balance) > 0 && <p className="text-amber-600 font-semibold">Owes KSh {Number(c.outstanding_balance).toFixed(0)}</p>}
                {Number(c.store_credit_balance) > 0 && <p className="text-brand-600">Credit KSh {Number(c.store_credit_balance).toFixed(0)}</p>}
              </div>
            </li>
          ))}
        </ul>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form onSubmit={handleSubmit} className="card w-full max-w-sm p-6">
            <h2 className="text-xl font-bold mb-4">Add customer</h2>
            <div className="space-y-3">
              <input required autoFocus className="input" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              <input className="input" placeholder="Phone (optional)" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div className="flex gap-3 mt-6">
              <button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" disabled={saving} className="btn-primary flex-1">{saving ? "Saving…" : "Save"}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
