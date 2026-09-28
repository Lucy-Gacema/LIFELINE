import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import SyncStatusBadge from "./SyncStatusBadge.jsx";

const ALL_NAV_ITEMS = [
  { to: "/sell", label: "Sell", icon: "🛒", roles: ["Admin", "Manager", "Cashier"] },
  { to: "/dashboard", label: "Business Today", icon: "📈", roles: ["Admin", "Manager"] },
  { to: "/products", label: "Products", icon: "🏷️", roles: ["Admin", "Manager"] },
  { to: "/customers", label: "Customers", icon: "👥", roles: ["Admin", "Manager", "Cashier"] },
  { to: "/sales", label: "Sales", icon: "🧾", roles: ["Admin", "Manager", "Cashier"] },
  { to: "/inventory", label: "Inventory", icon: "📦", roles: ["Admin", "Manager"] },
  { to: "/suppliers", label: "Suppliers", icon: "🚚", roles: ["Admin", "Manager"] },
  { to: "/reports", label: "Reports", icon: "📊", roles: ["Admin", "Manager"] },
  { to: "/assistant", label: "Business Assistant", icon: "💬", roles: ["Admin", "Manager", "Cashier"] },
  { to: "/settings", label: "Settings", icon: "⚙️", roles: ["Admin", "Manager"] },
];

export default function AppShell({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const navItems = ALL_NAV_ITEMS.filter((item) => !user || item.roles.includes(user.role));

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-gray-50">
      
      <header className="lg:hidden flex items-center justify-between px-4 py-3 bg-white border-b sticky top-0 z-30">
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          className="min-h-touch min-w-[3.5rem] flex items-center justify-center text-2xl"
          aria-label="Open menu"
        >
          ☰
        </button>
        <span className="font-bold text-brand-700 text-lg">LIFELINE</span>
        <SyncStatusBadge compact />
      </header>

      <nav
        className={`fixed lg:static inset-0 z-40 lg:z-auto bg-white lg:w-64 lg:flex-shrink-0 border-r flex flex-col ${
          menuOpen ? "flex" : "hidden lg:flex"
        }`}
        aria-label="Main navigation"
      >
        <div className="flex items-center justify-between px-5 py-5 border-b">
          <span className="font-extrabold text-brand-700 text-xl">LIFELINE</span>
          <button type="button" className="lg:hidden text-2xl" onClick={() => setMenuOpen(false)} aria-label="Close menu">
            ×
          </button>
        </div>
        <div className="px-4 py-3 hidden lg:block">
          <SyncStatusBadge />
        </div>
        <ul className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-3 text-lg font-medium min-h-touch ${
                    isActive ? "bg-brand-50 text-brand-700" : "text-gray-700 hover:bg-gray-100"
                  }`
                }
              >
                <span aria-hidden="true" className="text-xl">{item.icon}</span>
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
        <div className="border-t px-4 py-4">
          <p className="text-sm text-gray-500">Signed in as</p>
          <p className="font-semibold">{user?.first_name} {user?.last_name} <span className="text-gray-400 font-normal">({user?.role})</span></p>
          <button type="button" onClick={handleLogout} className="btn-secondary w-full mt-3">
            Switch user / Log out
          </button>
        </div>
      </nav>

      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
