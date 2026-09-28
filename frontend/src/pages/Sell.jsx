import React, { useEffect, useState, useCallback } from "react";
import { useAuth } from "../hooks/useAuth.jsx";
import * as productsApi from "../api/products.js";
import * as salesApi from "../api/sales.js";
import * as customersApi from "../api/customers.js";
import { cacheProducts, getCachedProducts, kvGet, kvSet, kvDelete, queueOperation, saveLocalSale, newIdempotencyKey } from "../db/index.js";
import { syncNow } from "../db/sync.js";
import ShiftGate from "../components/ShiftGate.jsx";
import ProductGrid from "../components/ProductGrid.jsx";
import CartPanel from "../components/CartPanel.jsx";
import PaymentModal from "../components/PaymentModal.jsx";
import ReceiptView from "../components/ReceiptView.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import Loading from "../components/Loading.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";

const CART_DRAFT_KEY = "cart_draft";
const HELD_SALES_KEY = "held_sales_local";

export default function Sell() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState([]);
  const [customer, setCustomer] = useState(null);
  const [customerQuery, setCustomerQuery] = useState("");
  const [customerResults, setCustomerResults] = useState([]);
  const [showCustomerSearch, setShowCustomerSearch] = useState(false);
  const [discount, setDiscount] = useState(0);
  const [showPayment, setShowPayment] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [lastSale, setLastSale] = useState(null);
  const [lastSaleOffline, setLastSaleOffline] = useState(false);
  const [heldSales, setHeldSales] = useState([]);
  const [showHeld, setShowHeld] = useState(false);
  const [clearConfirmOpen, setClearConfirmOpen] = useState(false);

  // --- Initial load: products + categories (cache-first fallback) ---
  useEffect(() => {
    (async () => {
      try {
        const [freshProducts, freshCategories] = await Promise.all([
          productsApi.listProducts(),
          productsApi.listCategories(),
        ]);
        setProducts(freshProducts);
        setCategories(freshCategories);
        cacheProducts(freshProducts);
      } catch {
        const cached = await getCachedProducts();
        setProducts(cached);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    })();

    kvGet(CART_DRAFT_KEY).then((draft) => {
      if (draft?.cart?.length) {
        setCart(draft.cart);
        setDiscount(draft.discount || 0);
        setCustomer(draft.customer || null);
      }
    });

    kvGet(HELD_SALES_KEY).then((held) => setHeldSales(held || []));
  }, []);

  useEffect(() => {
    if (cart.length === 0 && discount === 0 && !customer) {
      kvDelete(CART_DRAFT_KEY);
    } else {
      kvSet(CART_DRAFT_KEY, { cart, discount, customer });
    }
  }, [cart, discount, customer]);

  const addToCart = useCallback((product) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.key === product.product_id);
      if (existing) {
        return prev.map((i) => (i.key === product.product_id ? { ...i, quantity: i.quantity + 1 } : i));
      }
      return [
        ...prev,
        {
          key: product.product_id,
          product_id: product.product_id,
          product_name: product.product_name,
          unit_price: Number(product.selling_price),
          quantity: 1,
        },
      ];
    });
  }, []);

  const increase = (key) => setCart((prev) => prev.map((i) => (i.key === key ? { ...i, quantity: i.quantity + 1 } : i)));
  const decrease = (key) =>
    setCart((prev) => prev.map((i) => (i.key === key ? { ...i, quantity: Math.max(i.quantity - 1, 1) } : i)));
  const removeItem = (key) => setCart((prev) => prev.filter((i) => i.key !== key));

  const resetCart = () => {
    setCart([]);
    setDiscount(0);
    setCustomer(null);
  };

  const subtotal = cart.reduce((s, i) => s + i.unit_price * i.quantity, 0);
  const total = Math.max(subtotal - discount, 0);

  // --- Customer search ---
  useEffect(() => {
    if (!showCustomerSearch || !customerQuery.trim()) {
      setCustomerResults([]);
      return;
    }
    const t = setTimeout(() => {
      customersApi.listCustomers(customerQuery).then(setCustomerResults).catch(() => setCustomerResults([]));
    }, 250);
    return () => clearTimeout(t);
  }, [customerQuery, showCustomerSearch]);

  // --- Hold / resume ---
  const handleHold = async () => {
    const label = customer?.name || `Sale — ${new Date().toLocaleTimeString()}`;
    const snapshot = { cart, discount, customer };
    const entry = { held_sale_id: newIdempotencyKey(), label, snapshot, created_at: new Date().toISOString() };
    const updated = [entry, ...heldSales];
    setHeldSales(updated);
    await kvSet(HELD_SALES_KEY, updated);
    resetCart();
  };

  const handleResume = async (entry) => {
    setCart(entry.snapshot.cart);
    setDiscount(entry.snapshot.discount || 0);
    setCustomer(entry.snapshot.customer || null);
    const updated = heldSales.filter((h) => h.held_sale_id !== entry.held_sale_id);
    setHeldSales(updated);
    await kvSet(HELD_SALES_KEY, updated);
    setShowHeld(false);
  };

  // --- Checkout ---
  const handlePaymentConfirm = async (payments) => {
    const paidSum = payments.reduce((s, p) => s + p.amount, 0);
    const remaining = total - paidSum;

    if (remaining > 0.01 && !customer) {
      setError("Please add a customer first — the remaining balance needs somewhere to go on credit.");
      return;
    }

    setSubmitting(true);
    setError("");
    const idempotency_key = newIdempotencyKey();
    const payload = {
      idempotency_key,
      items: cart.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
      payments: payments.map((p) => ({
        method: p.method,
        amount: p.amount,
        amount_tendered: p.amount_tendered,
        transaction_reference: p.transaction_reference,
      })),
      customer_id: customer?.customer_id,
      discount_total: discount,
      created_via: "manual",
      device_id: "web",
    };

    try {
      const sale = await salesApi.createSale(payload);
      setLastSale({
        items: sale.items.map((i) => ({ product_name: i.product_name_snapshot, quantity: i.quantity, line_total: Number(i.line_total) })),
        total_amount: Number(sale.total_amount),
        receipt_number: sale.receipt_number,
      });
      setLastSaleOffline(false);
      resetCart();
      setShowPayment(false);
      // Refresh product cache stock quietly.
      productsApi.listProducts().then((p) => { setProducts(p); cacheProducts(p); }).catch(() => {});
    } catch (err) {
      if (err.status === 0) {
        // Offline: queue it, save a local receipt, optimistically adjust cached stock.
        await queueOperation({ device_id: "web", idempotency_key, operation_type: "create_sale", payload });
        const localSale = {
          idempotency_key,
          items: cart.map((i) => ({ product_name: i.product_name, quantity: i.quantity, line_total: i.unit_price * i.quantity })),
          total_amount: total,
          receipt_number: null,
        };
        await saveLocalSale(localSale);
        setProducts((prev) =>
          prev.map((p) => {
            const cartItem = cart.find((i) => i.product_id === p.product_id);
            return cartItem ? { ...p, current_stock: p.current_stock - cartItem.quantity } : p;
          })
        );
        setLastSale(localSale);
        setLastSaleOffline(true);
        resetCart();
        setShowPayment(false);
      } else {
        setError(err.message || "Could not record the sale. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loading label="Loading your products…" />;

  return (
    <ShiftGate>
      <div className="flex flex-col lg:flex-row h-[calc(100vh-56px)] lg:h-screen">
        <div className="flex-1 min-w-0 flex flex-col">
          {error && (
            <div className="p-4 pb-0">
              <ErrorBanner message={error} onDismiss={() => setError("")} />
            </div>
          )}
          {heldSales.length > 0 && (
            <div className="px-4 pt-3">
              <button type="button" onClick={() => setShowHeld(true)} className="btn-secondary w-full sm:w-auto">
                ⏸ {heldSales.length} held sale{heldSales.length > 1 ? "s" : ""} — tap to resume
              </button>
            </div>
          )}
          <div className="flex-1 min-h-0">
            <ProductGrid products={products} categories={categories} onAdd={addToCart} />
          </div>
        </div>

        <div className="w-full lg:w-96 flex-shrink-0 h-[45vh] lg:h-auto">
          {!customer && (
            <div className="px-4 pt-3 lg:pt-4">
              <button type="button" className="btn-secondary w-full" onClick={() => setShowCustomerSearch(true)}>
                + Add customer (optional)
              </button>
            </div>
          )}
          <CartPanel
            cart={cart}
            onIncrease={increase}
            onDecrease={decrease}
            onRemove={removeItem}
            customer={customer}
            onRemoveCustomer={() => setCustomer(null)}
            discount={discount}
            onCheckout={() => setShowPayment(true)}
            onHold={handleHold}
            onClear={() => setClearConfirmOpen(true)}
            disabled={submitting}
          />
        </div>
      </div>

      {showPayment && (
        <PaymentModal total={total} onClose={() => setShowPayment(false)} onConfirm={handlePaymentConfirm} submitting={submitting} />
      )}

      {lastSale && (
        <ReceiptView sale={lastSale} offline={lastSaleOffline} onNewSale={() => setLastSale(null)} />
      )}

      {showCustomerSearch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="card w-full max-w-sm p-6">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-lg font-bold">Find customer</h2>
              <button type="button" onClick={() => setShowCustomerSearch(false)} className="text-2xl" aria-label="Close">×</button>
            </div>
            <input autoFocus type="search" className="input" placeholder="Name or phone" value={customerQuery} onChange={(e) => setCustomerQuery(e.target.value)} />
            <ul className="mt-3 max-h-64 overflow-y-auto divide-y">
              {customerResults.map((c) => (
                <li key={c.customer_id}>
                  <button
                    type="button"
                    className="w-full text-left py-3"
                    onClick={() => { setCustomer(c); setShowCustomerSearch(false); setCustomerQuery(""); }}
                  >
                    <span className="font-medium">{c.name}</span>
                    {c.phone && <span className="text-gray-400 ml-2 text-sm">{c.phone}</span>}
                  </button>
                </li>
              ))}
              {customerQuery && customerResults.length === 0 && (
                <li className="py-3 text-gray-500 text-sm">No matches. You can add this customer from the Customers page.</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {showHeld && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="card w-full max-w-sm p-6">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-lg font-bold">Held sales</h2>
              <button type="button" onClick={() => setShowHeld(false)} className="text-2xl" aria-label="Close">×</button>
            </div>
            <ul className="divide-y">
              {heldSales.map((h) => (
                <li key={h.held_sale_id} className="py-3 flex justify-between items-center">
                  <div>
                    <p className="font-medium">{h.label}</p>
                    <p className="text-xs text-gray-400">{new Date(h.created_at).toLocaleTimeString()}</p>
                  </div>
                  <button type="button" className="btn-primary" onClick={() => handleResume(h)}>Resume</button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={clearConfirmOpen}
        title="Clear this sale?"
        description="Everything in the cart will be removed. This can't be undone."
        confirmLabel="Clear cart"
        danger
        onCancel={() => setClearConfirmOpen(false)}
        onConfirm={() => { resetCart(); setClearConfirmOpen(false); }}
      />
    </ShiftGate>
  );
}
