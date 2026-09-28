import React, { useEffect, useState } from "react";
import * as productsApi from "../api/products.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import Loading from "../components/Loading.jsx";
import EmptyState from "../components/EmptyState.jsx";

const emptyForm = {
  product_name: "", selling_price: "", current_stock: "",
  sku: "", barcode: "", buying_price: "", minimum_stock: "", unit: "pc", aliases: "",
};

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    productsApi
      .listProducts({ include_inactive: false })
      .then(setProducts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = products.filter((p) => p.product_name.toLowerCase().includes(search.toLowerCase()));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = {
        product_name: form.product_name,
        selling_price: Number(form.selling_price),
        current_stock: Number(form.current_stock) || 0,
      };
      if (form.sku) payload.sku = form.sku;
      if (form.barcode) payload.barcode = form.barcode;
      if (form.buying_price) payload.buying_price = Number(form.buying_price);
      if (form.minimum_stock) payload.minimum_stock = Number(form.minimum_stock);
      if (form.unit) payload.unit = form.unit;
      if (form.aliases) payload.aliases = form.aliases.split(",").map((a) => a.trim()).filter(Boolean);

      await productsApi.createProduct(payload);
      setForm(emptyForm);
      setShowForm(false);
      setShowAdvanced(false);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Products</h1>
        <button type="button" className="btn-primary" onClick={() => setShowForm(true)}>+ Add product</button>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError("")} />

      <input className="input mb-4" placeholder="Search products…" value={search} onChange={(e) => setSearch(e.target.value)} />

      {loading ? (
        <Loading />
      ) : filtered.length === 0 ? (
        <EmptyState icon="🏷️" title="No products yet" description="Add your first product to start selling." action={<button className="btn-primary" onClick={() => setShowForm(true)}>+ Add product</button>} />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-sm text-gray-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Price</th>
                <th className="px-4 py-3">Stock</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map((p) => (
                <tr key={p.product_id}>
                  <td className="px-4 py-3 font-medium">{p.product_name}</td>
                  <td className="px-4 py-3">KSh {Number(p.selling_price).toFixed(0)}</td>
                  <td className="px-4 py-3">{p.current_stock} {p.unit}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      p.stock_status === "out_of_stock" ? "bg-red-100 text-red-700" :
                      p.stock_status === "critical" ? "bg-red-50 text-red-600" :
                      p.stock_status === "low" ? "bg-amber-50 text-amber-700" : "bg-brand-50 text-brand-700"
                    }`}>
                      {p.stock_status.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 p-0 sm:p-4">
          <form onSubmit={handleSubmit} className="card w-full sm:max-w-md rounded-b-none sm:rounded-2xl max-h-[95vh] overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Add product</h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-2xl" aria-label="Close">×</button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Product name *</label>
                <input required className="input" value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })} autoFocus />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Selling price *</label>
                  <input required type="number" min="0" step="0.01" className="input" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Starting stock</label>
                  <input type="number" min="0" className="input" value={form.current_stock} onChange={(e) => setForm({ ...form, current_stock: e.target.value })} />
                </div>
              </div>

              {!showAdvanced ? (
                <button type="button" className="text-brand-700 font-medium text-sm" onClick={() => setShowAdvanced(true)}>
                  + Add more details (optional)
                </button>
              ) : (
                <div className="space-y-3 pt-2 border-t">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Cost price</label>
                      <input type="number" min="0" step="0.01" className="input" value={form.buying_price} onChange={(e) => setForm({ ...form, buying_price: e.target.value })} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Minimum stock</label>
                      <input type="number" min="0" className="input" value={form.minimum_stock} onChange={(e) => setForm({ ...form, minimum_stock: e.target.value })} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">SKU</label>
                      <input className="input" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-1">Barcode</label>
                      <input className="input" value={form.barcode} onChange={(e) => setForm({ ...form, barcode: e.target.value })} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Unit</label>
                    <select className="input" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })}>
                      {["pc", "packet", "kg", "litre", "bottle", "loaf", "tub", "box"].map((u) => <option key={u} value={u}>{u}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">Nicknames / aliases (comma-separated)</label>
                    <input className="input" placeholder="e.g. blueband, blue, margarine" value={form.aliases} onChange={(e) => setForm({ ...form, aliases: e.target.value })} />
                  </div>
                </div>
              )}
            </div>

            <button type="submit" disabled={saving} className="btn-primary w-full mt-6">
              {saving ? "Saving…" : "Save product"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
