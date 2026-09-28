import React, { useMemo, useState } from "react";


export default function ProductGrid({ products, onAdd, categories }) {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState(null);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(true);

  const filtered = useMemo(() => {
    let list = products;
    if (activeCategory) list = list.filter((p) => p.category_id === activeCategory);
    if (showFavoritesOnly && !query) list = list.filter((p) => p.is_favorite);

    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter((p) => {
        const haystacks = [p.product_name, p.sku, p.barcode, ...(p.aliases || [])].filter(Boolean).map((s) => s.toLowerCase());
        return haystacks.some((h) => h.includes(q));
      });
    }
    return list;
  }, [products, query, activeCategory, showFavoritesOnly]);

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b bg-white sticky top-0 z-10">
        <label htmlFor="product-search" className="sr-only">Search products</label>
        <input
          id="product-search"
          type="search"
          inputMode="search"
          placeholder="Search by name, SKU, barcode…"
          className="input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
          <button
            type="button"
            onClick={() => { setActiveCategory(null); setShowFavoritesOnly(true); }}
            className={`px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap min-h-[2.5rem] ${!activeCategory && showFavoritesOnly ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            ⭐ Favorites
          </button>
          <button
            type="button"
            onClick={() => { setActiveCategory(null); setShowFavoritesOnly(false); }}
            className={`px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap min-h-[2.5rem] ${!activeCategory && !showFavoritesOnly ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.category_id}
              type="button"
              onClick={() => { setActiveCategory(c.category_id); setShowFavoritesOnly(false); }}
              className={`px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap min-h-[2.5rem] ${activeCategory === c.category_id ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-700"}`}
            >
              {c.icon} {c.name}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {filtered.length === 0 ? (
          <p className="text-center text-gray-500 py-12">
            {query ? `No products match "${query}".` : "No products here yet. Add some from the Products page."}
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {filtered.map((p) => (
              <button
                key={p.product_id}
                type="button"
                onClick={() => onAdd(p)}
                disabled={p.current_stock <= 0}
                className="card p-4 flex flex-col items-start text-left hover:border-brand-400 hover:shadow-md transition min-h-[7rem] disabled:opacity-40"
              >
                <span className="font-semibold text-gray-900 leading-snug">{p.product_name}</span>
                <span className="text-brand-700 font-bold text-lg mt-1">KSh {Number(p.selling_price).toFixed(0)}</span>
                <span className={`text-xs mt-1 font-medium ${
                  p.stock_status === "out_of_stock" ? "text-red-600" : p.stock_status === "critical" || p.stock_status === "low" ? "text-amber-600" : "text-gray-400"
                }`}>
                  {p.current_stock <= 0 ? "Out of stock" : `${p.current_stock} in stock`}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
