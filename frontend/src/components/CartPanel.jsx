import React from "react";

export default function CartPanel({ cart, onIncrease, onDecrease, onRemove, customer, onRemoveCustomer, note, discount, onCheckout, onHold, onClear, disabled }) {
  const subtotal = cart.reduce((sum, item) => sum + item.unit_price * item.quantity, 0);
  const total = Math.max(subtotal - discount, 0);
  const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="flex flex-col h-full bg-white border-l">
      <div className="px-4 py-3 border-b flex items-center justify-between">
        <h2 className="font-bold text-lg">Cart {itemCount > 0 && <span className="text-gray-400 font-normal">({itemCount})</span>}</h2>
        {cart.length > 0 && (
          <button type="button" onClick={onClear} className="text-sm text-red-600 font-medium">
            Clear
          </button>
        )}
      </div>

      {customer && (
        <div className="mx-4 mt-3 flex items-center justify-between bg-brand-50 text-brand-800 rounded-xl px-3 py-2 text-sm">
          <span>👤 {customer.name}</span>
          <button type="button" onClick={onRemoveCustomer} className="font-bold" aria-label="Remove customer">×</button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-4 py-2">
        {cart.length === 0 ? (
          <p className="text-center text-gray-400 py-12">Tap a product to add it here.</p>
        ) : (
          <ul className="divide-y">
            {cart.map((item) => (
              <li key={item.key} className="py-3">
                <div className="flex justify-between items-start gap-2">
                  <div className="min-w-0">
                    <p className="font-medium truncate">{item.product_name}</p>
                    <p className="text-sm text-gray-500">KSh {item.unit_price.toFixed(0)} each</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button type="button" onClick={() => onDecrease(item.key)} className="h-9 w-9 rounded-full bg-gray-100 text-lg font-bold" aria-label={`Decrease ${item.product_name}`}>−</button>
                    <span className="w-6 text-center font-semibold" aria-live="polite">{item.quantity}</span>
                    <button type="button" onClick={() => onIncrease(item.key)} className="h-9 w-9 rounded-full bg-gray-100 text-lg font-bold" aria-label={`Increase ${item.product_name}`}>+</button>
                  </div>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <button type="button" onClick={() => onRemove(item.key)} className="text-xs text-red-500">Remove</button>
                  <span className="font-semibold">KSh {(item.unit_price * item.quantity).toFixed(0)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="border-t px-4 py-4 space-y-2">
        {discount > 0 && (
          <div className="flex justify-between text-sm text-gray-600">
            <span>Discount</span>
            <span>− KSh {discount.toFixed(0)}</span>
          </div>
        )}
        <div className="flex justify-between text-xl font-extrabold">
          <span>Total</span>
          <span>KSh {total.toFixed(0)}</span>
        </div>
        <div className="grid grid-cols-2 gap-2 pt-2">
          <button type="button" onClick={onHold} disabled={cart.length === 0 || disabled} className="btn-secondary">
            Hold sale
          </button>
          <button type="button" onClick={onCheckout} disabled={cart.length === 0 || disabled} className="btn-primary text-lg">
            Charge
          </button>
        </div>
      </div>
    </div>
  );
}
