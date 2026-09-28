import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as reportsApi from "../api/reports.js";
import { useAuth } from "../hooks/useAuth.jsx";
import Loading from "../components/Loading.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

function StatCard({ label, value, sub }) {
  return (
    <div className="card p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-extrabold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const { hasPermission } = useAuth();
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    reportsApi.getBusinessHealth().then(setHealth).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading label="Checking how business is going…" />;
  if (error) return <div className="p-6"><ErrorBanner message={error} /></div>;
  if (!health) return null;

  const canViewProfit = hasPermission("view_profit");

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6">
      <h1 className="text-2xl font-bold mb-1">How is my business doing?</h1>
      <p className="text-gray-500 mb-6">{health.today.period}</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <StatCard label="Sales today" value={`KSh ${health.today.total_sales.toFixed(0)}`} sub={`${health.today.transaction_count} transactions`} />
        {canViewProfit ? (
          <StatCard label="Profit today" value={`KSh ${health.profit_today.gross_profit.toFixed(0)}`} sub="Estimated, based on recorded cost prices" />
        ) : (
          <StatCard label="Avg. sale" value={`KSh ${health.today.average_transaction.toFixed(0)}`} />
        )}
        <StatCard label="Low / out of stock" value={health.low_stock_products.length} sub={`${health.out_of_stock_count} fully out`} />
        <StatCard label="Customers owe you" value={`KSh ${health.outstanding_customer_credit.toFixed(0)}`} />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card p-4">
          <h2 className="font-bold mb-3">Best sellers today</h2>
          {health.top_products_today.length === 0 ? (
            <p className="text-gray-400 text-sm">No sales recorded yet today.</p>
          ) : (
            <ul className="divide-y">
              {health.top_products_today.map((p, i) => (
                <li key={i} className="py-2 flex justify-between">
                  <span>{p.name}</span>
                  <span className="text-gray-500">{p.quantity} sold</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card p-4">
          <h2 className="font-bold mb-3">Needs attention</h2>
          {health.low_stock_products.length === 0 ? (
            <p className="text-gray-400 text-sm">Nothing is low on stock. 🎉</p>
          ) : (
            <ul className="divide-y">
              {health.low_stock_products.slice(0, 6).map((p, i) => (
                <li key={i} className="py-2 flex justify-between">
                  <span>{p.name}</span>
                  <span className={p.current_stock <= 0 ? "text-red-600 font-semibold" : "text-amber-600"}>
                    {p.current_stock} left
                  </span>
                </li>
              ))}
            </ul>
          )}
          <Link to="/inventory" className="text-brand-700 font-medium text-sm mt-3 inline-block">View all inventory →</Link>
        </div>
      </div>

      {health.supplier_balances_owed > 0 && (
        <div className="card p-4 mt-4 flex justify-between items-center">
          <span className="font-medium">You owe suppliers</span>
          <span className="font-bold text-amber-600">KSh {health.supplier_balances_owed.toFixed(0)}</span>
        </div>
      )}
    </div>
  );
}
