import React, { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth.jsx";
import { initSyncEngine } from "./db/sync.js";
import AppShell from "./components/AppShell.jsx";

import Login from "./pages/Login.jsx";
import Sell from "./pages/Sell.jsx";
import Products from "./pages/Products.jsx";
import Customers from "./pages/Customers.jsx";
import SalesHistory from "./pages/SalesHistory.jsx";
import Inventory from "./pages/Inventory.jsx";
import Suppliers from "./pages/Suppliers.jsx";
import Reports from "./pages/Reports.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Assistant from "./pages/Assistant.jsx";
import Settings from "./pages/Settings.jsx";

function ProtectedRoute({ children, permission }) {
  const { isAuthenticated, hasPermission } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (permission && !hasPermission(permission)) {
    return (
      <div className="max-w-md mx-auto p-8 text-center">
        <p className="text-4xl mb-3">🔒</p>
        <p className="text-gray-600">You don't have permission to view this page.</p>
      </div>
    );
  }
  return <AppShell>{children}</AppShell>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/sell" element={<ProtectedRoute><Sell /></ProtectedRoute>} />
      <Route path="/products" element={<ProtectedRoute permission="edit_products"><Products /></ProtectedRoute>} />
      <Route path="/customers" element={<ProtectedRoute><Customers /></ProtectedRoute>} />
      <Route path="/sales" element={<ProtectedRoute><SalesHistory /></ProtectedRoute>} />
      <Route path="/inventory" element={<ProtectedRoute permission="adjust_inventory"><Inventory /></ProtectedRoute>} />
      <Route path="/suppliers" element={<ProtectedRoute permission="manage_suppliers"><Suppliers /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute permission="access_reports"><Reports /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/assistant" element={<ProtectedRoute><Assistant /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/sell" replace />} />
    </Routes>
  );
}

export default function App() {
  useEffect(() => {
    initSyncEngine();
  }, []);

  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
