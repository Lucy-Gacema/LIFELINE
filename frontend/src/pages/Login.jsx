import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import * as authApi from "../api/auth.js";
import NumericKeypad from "../components/NumericKeypad.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

export default function Login() {
  const { loginWithPassword, loginWithPin, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("pin"); // "pin" | "password"
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [pin, setPin] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) navigate("/sell", { replace: true });
  }, [isAuthenticated]);

  useEffect(() => {
    authApi
      .getSwitchUserList()
      .then(setUsers)
      .catch(() => setUsers([])); // offline on first load: fall back to password mode silently
  }, []);

  const submitPin = async (fullPin) => {
    if (!selectedUser) return;
    setLoading(true);
    setError("");
    try {
      await loginWithPin(selectedUser.user_id, fullPin);
      navigate("/sell");
    } catch (err) {
      setError(err.message || "Incorrect PIN.");
      setPin("");
    } finally {
      setLoading(false);
    }
  };

  const onDigit = (d) => {
    const next = (pin + d).slice(0, 6);
    setPin(next);
    if (next.length >= 4) {
      // auto-submit once a plausible PIN length is reached feels fastest;
      // if it's wrong we simply clear and let them retry.
    }
  };

  const handlePinSubmit = (e) => {
    e.preventDefault();
    submitPin(pin);
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await loginWithPassword(email, password);
      navigate("/sell");
    } catch (err) {
      setError(err.message || "Incorrect email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-50 p-4">
      <div className="card w-full max-w-md p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-extrabold text-brand-700">LIFELINE</h1>
          <p className="text-gray-500 mt-1">Your simple shop assistant &amp; POS</p>
        </div>

        <ErrorBanner message={error} onDismiss={() => setError("")} />

        {mode === "pin" && !selectedUser && (
          <div>
            <p className="text-center font-medium text-gray-700 mb-3">Who's working?</p>
            {users.length === 0 ? (
              <p className="text-center text-gray-500 text-sm mb-3">
                No users loaded yet — {navigator.onLine ? "try again in a moment," : "you appear to be offline,"} or use email &amp; password below.
              </p>
            ) : (
              <div className="grid grid-cols-2 gap-3 mb-4">
                {users.map((u) => (
                  <button
                    key={u.user_id}
                    type="button"
                    onClick={() => setSelectedUser(u)}
                    className="btn-secondary flex-col h-24 text-base"
                  >
                    <span className="text-2xl mb-1" aria-hidden="true">👤</span>
                    {u.first_name}
                  </button>
                ))}
              </div>
            )}
            <button type="button" className="btn-primary w-full" onClick={() => setMode("password")}>
              Log in with email &amp; password
            </button>
          </div>
        )}

        {mode === "pin" && selectedUser && (
          <form onSubmit={handlePinSubmit}>
            <button type="button" onClick={() => { setSelectedUser(null); setPin(""); }} className="text-brand-700 font-medium mb-3">
              ← Not {selectedUser.first_name}?
            </button>
            <p className="text-center font-medium text-gray-700 mb-2">Enter PIN for {selectedUser.first_name}</p>
            <div className="flex justify-center gap-2 mb-4" aria-live="polite">
              {[0, 1, 2, 3].map((i) => (
                <span key={i} className={`h-4 w-4 rounded-full border-2 ${i < pin.length ? "bg-brand-600 border-brand-600" : "border-gray-300"}`} />
              ))}
            </div>
            <NumericKeypad
              disabled={loading}
              onDigit={onDigit}
              onBackspace={() => setPin(pin.slice(0, -1))}
              onClear={() => setPin("")}
            />
            <button type="submit" disabled={loading || pin.length < 4} className="btn-primary w-full mt-4">
              {loading ? "Checking…" : "Log in"}
            </button>
          </form>
        )}

        {mode === "password" && (
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block font-medium text-gray-700 mb-1">Email</label>
              <input id="email" type="email" required autoComplete="username" className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div>
              <label htmlFor="password" className="block font-medium text-gray-700 mb-1">Password</label>
              <input id="password" type="password" required autoComplete="current-password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? "Logging in…" : "Log in"}
            </button>
            <button type="button" className="text-brand-700 font-medium w-full text-center" onClick={() => setMode("pin")}>
              ← Back to PIN login
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
