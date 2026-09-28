import React from "react";

export default function ReceiptView({ sale, businessName = "My Shop", onNewSale, offline }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="card w-full max-w-sm p-6 text-center">
        <div className="text-5xl mb-2" aria-hidden="true">✅</div>
        <h2 className="text-2xl font-bold mb-1">Sale recorded</h2>
        {offline && (
          <p className="text-amber-600 text-sm mb-2">Saved offline — will sync automatically when you're back online.</p>
        )}
        <p className="text-gray-500 mb-4">{businessName}</p>

        <div className="text-left border-y py-3 my-3 divide-y">
          {sale.items.map((item, i) => (
            <div key={i} className="flex justify-between py-1.5 text-sm">
              <span>{item.quantity} × {item.product_name}</span>
              <span>KSh {item.line_total.toFixed(0)}</span>
            </div>
          ))}
        </div>

        <div className="flex justify-between text-xl font-extrabold mb-4">
          <span>Total</span>
          <span>KSh {sale.total_amount.toFixed(0)}</span>
        </div>

        <p className="text-xs text-gray-400 mb-4">Receipt {sale.receipt_number || "(pending sync)"}</p>

        <div className="grid grid-cols-2 gap-3">
          <button type="button" className="btn-secondary" onClick={() => window.print()}>
            Print
          </button>
          <button type="button" className="btn-primary" onClick={onNewSale} autoFocus>
            New sale
          </button>
        </div>
      </div>
    </div>
  );
}
