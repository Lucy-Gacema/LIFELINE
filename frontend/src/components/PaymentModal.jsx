import React, { useMemo, useState } from "react";

const METHODS = [
  { key: "cash", label: "Cash", icon: "💵" },
  { key: "mpesa", label: "M-Pesa", icon: "📱" },
  { key: "card", label: "Card", icon: "💳" },
  { key: "wallet", label: "Wallet", icon: "👛" },
  { key: "custom", label: "Other", icon: "➕" },
];


export default function PaymentModal({ total, onClose, onConfirm, submitting }) {
  const [payments, setPayments] = useState([]);
  const [activeMethod, setActiveMethod] = useState("cash");
  const [amountInput, setAmountInput] = useState(String(total));
  const [tenderedInput, setTenderedInput] = useState("");
  const [reference, setReference] = useState("");

  const paidSoFar = payments.reduce((s, p) => s + p.amount, 0);
  const remaining = Math.max(total - paidSoFar, 0);

  const change = useMemo(() => {
    const tendered = Number(tenderedInput) || 0;
    const amount = Number(amountInput) || 0;
    return Math.max(tendered - amount, 0);
  }, [tenderedInput, amountInput]);

  const addPayment = () => {
    const amount = Number(amountInput);
    if (!amount || amount <= 0) return;
    const entry = { method: activeMethod, amount };
    if (activeMethod === "cash") {
      entry.amount_tendered = Number(tenderedInput) || amount;
    }
    if (activeMethod === "mpesa" && reference) {
      entry.transaction_reference = reference;
    }
    setPayments([...payments, entry]);
    const nextRemaining = Math.max(remaining - amount, 0);
    setAmountInput(nextRemaining > 0 ? String(nextRemaining) : "0");
    setTenderedInput("");
    setReference("");
  };

  const removePayment = (idx) => setPayments(payments.filter((_, i) => i !== idx));

  const canFinalize = paidSoFar >= total - 0.01 || payments.length > 0; // allow partial -> credit, handled by parent

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 p-0 sm:p-4">
      <div className="card w-full sm:max-w-lg rounded-b-none sm:rounded-2xl max-h-[95vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Take payment</h2>
          <button type="button" onClick={onClose} className="text-2xl leading-none" aria-label="Close">×</button>
        </div>

        <div className="text-center mb-4">
          <p className="text-gray-500">Total due</p>
          <p className="text-4xl font-extrabold">KSh {total.toFixed(0)}</p>
          {remaining > 0 && payments.length > 0 && (
            <p className="text-amber-600 font-medium mt-1">KSh {remaining.toFixed(0)} remaining</p>
          )}
        </div>

        {payments.length > 0 && (
          <ul className="mb-4 space-y-2">
            {payments.map((p, i) => (
              <li key={i} className="flex justify-between items-center bg-gray-50 rounded-xl px-3 py-2">
                <span className="capitalize">{p.method} — KSh {p.amount.toFixed(0)}</span>
                <button type="button" onClick={() => removePayment(i)} className="text-red-500 text-sm font-medium">Remove</button>
              </li>
            ))}
          </ul>
        )}

        <div className="grid grid-cols-5 gap-2 mb-4">
          {METHODS.map((m) => (
            <button
              key={m.key}
              type="button"
              onClick={() => setActiveMethod(m.key)}
              className={`flex flex-col items-center justify-center rounded-xl py-3 text-xs font-semibold min-h-touch ${
                activeMethod === m.key ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-700"
              }`}
            >
              <span className="text-xl mb-1" aria-hidden="true">{m.icon}</span>
              {m.label}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Amount</label>
            <input type="number" inputMode="decimal" className="input text-xl" value={amountInput} onChange={(e) => setAmountInput(e.target.value)} />
          </div>

          {activeMethod === "cash" && (
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Customer gave</label>
              <input type="number" inputMode="decimal" className="input text-xl" value={tenderedInput} onChange={(e) => setTenderedInput(e.target.value)} placeholder="0" />
              {Number(tenderedInput) > 0 && (
                <p className="mt-2 text-lg font-bold text-brand-700">Change: KSh {change.toFixed(0)}</p>
              )}
            </div>
          )}

          {activeMethod === "mpesa" && (
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">M-Pesa code (optional)</label>
              <input type="text" className="input" value={reference} onChange={(e) => setReference(e.target.value)} placeholder="e.g. QCH7X8Y9" />
              <p className="text-xs text-gray-400 mt-1">This is recorded as manually entered unless your M-Pesa integration is connected.</p>
            </div>
          )}

          <button type="button" onClick={addPayment} className="btn-secondary w-full">
            Add payment
          </button>
        </div>

        <button
          type="button"
          disabled={!canFinalize || submitting}
          onClick={() => onConfirm(payments)}
          className="btn-primary w-full mt-6 text-lg"
        >
          {submitting ? "Recording sale…" : remaining > 0.01 ? `Record sale (KSh ${remaining.toFixed(0)} on credit)` : "Record sale"}
        </button>
      </div>
    </div>
  );
}
