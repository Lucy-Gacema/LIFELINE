import React, { useEffect, useState } from "react";
import * as reportsApi from "../api/reports.js";
import { useAuth } from "../hooks/useAuth.jsx";
import Loading from "../components/Loading.jsx";

const PERIODS = [
  { key: "today", label: "Today" },
  { key: "yesterday", label: "Yesterday" },
  { key: "this_week", label: "This week" },
  { key: "last_week", label: "Last week" },
  { key: "this_month", label: "This month" },
];

export default function Reports() {
  const { hasPermission } = useAuth();
  const [period, setPeriod] = useState("today");
  const [sales, setSales] = useState(null);
  const [profit, setProfit] = useState(null);
  const [top, setTop] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const calls = [reportsApi.getSalesSummary(period), reportsApi.getTopProducts(period)];
    if (hasPermission("view_profit")) calls.push(reportsApi.getProfitSummary(period));
    Promise.all(calls)
      .then(([s, t, p]) => { setSales(s); setTop(t); setProfit(p || null); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [period]);

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      <h1 className="text-2xl font-bold mb-4">Reports</h1>
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {PERIODS.map((p) => (
          <button
            key={p.key}
            onClick={() => setPeriod(p.key)}
            className={`px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap ${period === p.key ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {loading || !sales ? <Loading /> : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="card p-4"><p className="text-sm text-gray-500">Total sales</p><p className="text-2xl font-extrabold">KSh {sales.total_sales.toFixed(0)}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-500">Transactions</p><p className="text-2xl font-extrabold">{sales.transaction_count}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-500">Avg. transaction</p><p className="text-2xl font-extrabold">KSh {sales.average_transaction.toFixed(0)}</p></div>
            {profit && <div className="card p-4"><p className="text-sm text-gray-500">Gross profit</p><p className="text-2xl font-extrabold">KSh {profit.gross_profit.toFixed(0)}</p></div>}
          </div>

          <div className="card p-4">
            <h2 className="font-bold mb-3">Payment methods</h2>
            {Object.keys(sales.payment_breakdown).length === 0 ? (
              <p className="text-gray-400 text-sm">No payments recorded for this period.</p>
            ) : (
              <ul className="divide-y">
                {Object.entries(sales.payment_breakdown).map(([method, amount]) => (
                  <li key={method} className="py-2 flex justify-between capitalize">
                    <span>{method}</span>
                    <span className="font-semibold">KSh {amount.toFixed(0)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="card p-4">
            <h2 className="font-bold mb-3">Top products</h2>
            {top.length === 0 ? (
              <p className="text-gray-400 text-sm">Nothing sold in this period yet.</p>
            ) : (
              <ul className="divide-y">
                {top.map((p, i) => (
                  <li key={i} className="py-2 flex justify-between">
                    <span>{p.name}</span>
                    <span className="text-gray-500">{p.quantity} sold — KSh {p.revenue.toFixed(0)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
