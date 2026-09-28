import React, { useEffect, useState } from "react";
import * as shiftsApi from "../api/shifts.js";
import Loading from "./Loading.jsx";
import ErrorBanner from "./ErrorBanner.jsx";

export default function ShiftGate({ children }) {
  const [loading, setLoading] = useState(true);
  const [shift, setShift] = useState(null);
  const [opening, setOpening] = useState(false);
  const [openingCash, setOpeningCash] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    shiftsApi
      .getCurrentShift()
      .then((s) => setShift(s))
      .catch(() => setShift({ shift_id: "offline-local", status: "open", opening_cash: 0, offline: true }))
      .finally(() => setLoading(false));
  }, []);

  const handleOpen = async (e) => {
    e.preventDefault();
    setOpening(true);
    setError("");
    try {
      const s = await shiftsApi.openShift(Number(openingCash) || 0);
      setShift(s);
    } catch (err) {
     
      setShift({ shift_id: "offline-local", status: "open", opening_cash: Number(openingCash) || 0, offline: true });
      setError(err.message + " Starting a local shift instead — it'll sync once you're back online.");
    } finally {
      setOpening(false);
    }
  };

  if (loading) return <Loading label="Checking your shift…" />;

  if (!shift) {
    return (
      <div className="max-w-md mx-auto p-6">
        <div className="card p-6">
          <h2 className="text-2xl font-bold mb-1">Open the till</h2>
          <p className="text-gray-500 mb-4">How much cash is in the drawer right now?</p>
          <ErrorBanner message={error} />
          <form onSubmit={handleOpen} className="space-y-4">
            <input
              type="number"
              inputMode="decimal"
              min="0"
              className="input text-2xl text-center"
              placeholder="0"
              value={openingCash}
              onChange={(e) => setOpeningCash(e.target.value)}
              autoFocus
            />
            <button type="submit" disabled={opening} className="btn-primary w-full text-lg">
              {opening ? "Opening…" : "Start selling"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return children;
}
