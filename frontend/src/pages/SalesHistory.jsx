import React, { useEffect, useState } from "react";
import * as salesApi from "../api/sales.js";
import Loading from "../components/Loading.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

export default function SalesHistory() {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    salesApi.listSales({ limit: 100 }).then(setSales).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      <h1 className="text-2xl font-bold mb-4">Sales history</h1>
      <ErrorBanner message={error} />
      {loading ? <Loading /> : sales.length === 0 ? (
        <EmptyState icon="🧾" title="No sales yet" description="Completed sales will show up here." />
      ) : (
        <ul className="card divide-y">
          {sales.map((s) => (
            <li key={s.sale_id}>
              <button type="button" onClick={() => setSelected(s)} className="w-full text-left px-4 py-3 flex justify-between items-center hover:bg-gray-50">
                <div>
                  <p className="font-semibold">{s.receipt_number || "Pending sync"}</p>
                  <p className="text-sm text-gray-500">{new Date(s.timestamp).toLocaleString()}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">KSh {Number(s.total_amount).toFixed(0)}</p>
                  <p className={`text-xs font-medium ${s.status === "completed" ? "text-brand-600" : "text-gray-400"}`}>{s.status}</p>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="card w-full max-w-sm p-6">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-lg font-bold">{selected.receipt_number}</h2>
              <button type="button" onClick={() => setSelected(null)} className="text-2xl" aria-label="Close">×</button>
            </div>
            <ul className="divide-y mb-3">
              {selected.items.map((i) => (
                <li key={i.sale_item_id} className="py-2 flex justify-between text-sm">
                  <span>{i.quantity} × {i.product_name_snapshot}</span>
                  <span>KSh {Number(i.line_total).toFixed(0)}</span>
                </li>
              ))}
            </ul>
            <div className="flex justify-between font-bold text-lg">
              <span>Total</span>
              <span>KSh {Number(selected.total_amount).toFixed(0)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
