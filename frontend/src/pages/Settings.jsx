import React, { useEffect, useState } from "react";
import * as settingsApi from "../api/settings.js";
import * as shiftsApi from "../api/shifts.js";
import { apiFetch } from "../api/client.js";
import { useAuth } from "../hooks/useAuth.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import Loading from "../components/Loading.jsx";

export default function Settings() {
  const { hasPermission } = useAuth();
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [shift, setShift] = useState(null);
  const [closeCash, setCloseCash] = useState("");
  const [closeConfirmOpen, setCloseConfirmOpen] = useState(false);
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ email: "", password: "", first_name: "", last_name: "", role: "Cashier" });

  useEffect(() => {
    settingsApi.getSettings().then(setSettings).catch((e) => setError(e.message));
    shiftsApi.getCurrentShift().then(setShift).catch(() => {});
    if (hasPermission("manage_users")) apiFetch("/api/v1/users/").then(setUsers).catch(() => {});
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const updated = await settingsApi.updateSettings(settings);
      setSettings(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleCloseShift = async () => {
    try {
      await shiftsApi.closeShift(shift.shift_id, { actual_cash: Number(closeCash) || 0 });
      setShift(null);
      setCloseConfirmOpen(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await apiFetch("/api/v1/users/", { method: "POST", body: JSON.stringify(newUser) });
      setNewUser({ email: "", password: "", first_name: "", last_name: "", role: "Cashier" });
      const updated = await apiFetch("/api/v1/users/");
      setUsers(updated);
    } catch (err) {
      setError(err.message);
    }
  };

  if (!settings) return <Loading />;

  return (
    <div className="max-w-3xl mx-auto p-4 sm:p-6 space-y-8">
      <h1 className="text-2xl font-bold">Settings</h1>
      <ErrorBanner message={error} onDismiss={() => setError("")} />

      {shift && (
        <div className="card p-5">
          <h2 className="font-bold text-lg mb-2">Current shift</h2>
          <p className="text-gray-500 mb-3">Opened with KSh {Number(shift.opening_cash).toFixed(0)}</p>
          <div className="flex gap-3 items-center">
            <input type="number" className="input" placeholder="Cash counted now" value={closeCash} onChange={(e) => setCloseCash(e.target.value)} />
            <button type="button" className="btn-danger whitespace-nowrap" onClick={() => setCloseConfirmOpen(true)}>Close shift</button>
          </div>
        </div>
      )}

      {hasPermission("change_settings") && (
        <form onSubmit={handleSaveSettings} className="card p-5 space-y-4">
          <h2 className="font-bold text-lg">Business details</h2>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Business name</label>
            <input className="input" value={settings.business_name} onChange={(e) => setSettings({ ...settings, business_name: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Phone</label>
              <input className="input" value={settings.phone || ""} onChange={(e) => setSettings({ ...settings, phone: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Currency</label>
              <input className="input" value={settings.currency} onChange={(e) => setSettings({ ...settings, currency: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Receipt footer message</label>
            <input className="input" value={settings.receipt_footer || ""} onChange={(e) => setSettings({ ...settings, receipt_footer: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Low stock threshold</label>
              <input type="number" className="input" value={settings.low_stock_threshold} onChange={(e) => setSettings({ ...settings, low_stock_threshold: Number(e.target.value) })} />
            </div>
            <div className="flex items-end pb-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <input type="checkbox" className="h-5 w-5" checked={settings.allow_negative_stock} onChange={(e) => setSettings({ ...settings, allow_negative_stock: e.target.checked })} />
                Allow selling below zero stock
              </label>
            </div>
          </div>
          <button type="submit" disabled={saving} className="btn-primary">{saving ? "Saving…" : "Save settings"}</button>
        </form>
      )}

      {hasPermission("manage_users") && (
        <div className="card p-5">
          <h2 className="font-bold text-lg mb-3">Team</h2>
          <ul className="divide-y mb-4">
            {users.map((u) => (
              <li key={u.user_id} className="py-2 flex justify-between">
                <span>{u.first_name} {u.last_name}</span>
                <span className="text-gray-400">{u.role}</span>
              </li>
            ))}
          </ul>
          <form onSubmit={handleAddUser} className="grid grid-cols-2 gap-3">
            <input required className="input" placeholder="First name" value={newUser.first_name} onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })} />
            <input required className="input" placeholder="Last name" value={newUser.last_name} onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })} />
            <input required type="email" className="input col-span-2" placeholder="Email" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
            <input required type="password" className="input" placeholder="Password" value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} />
            <select className="input" value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>
              <option value="Cashier">Cashier</option>
              <option value="Manager">Manager</option>
              <option value="Admin">Admin</option>
            </select>
            <button type="submit" className="btn-primary col-span-2">Add team member</button>
          </form>
        </div>
      )}

      <ConfirmDialog
        open={closeConfirmOpen}
        title="Close this shift?"
        description="This records the counted cash and any difference from what's expected. It can't be undone."
        confirmLabel="Close shift"
        danger
        onCancel={() => setCloseConfirmOpen(false)}
        onConfirm={handleCloseShift}
      />
    </div>
  );
}
