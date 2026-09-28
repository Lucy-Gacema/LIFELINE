import { apiFetch, setToken, setStoredUser } from "./client.js";

export async function loginWithPassword(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Incorrect email or password.");
  }
  const data = await res.json();
  setToken(data.access_token);
  setStoredUser(data.user);
  return data.user;
}

export async function loginWithPin(userId, pin) {
  const data = await apiFetch("/api/v1/auth/pin-login", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, pin }),
  });
  setToken(data.access_token);
  setStoredUser(data.user);
  return data.user;
}

export async function getSwitchUserList() {
  return apiFetch("/api/v1/auth/switch-user-list");
}

export function logout() {
  setToken(null);
  setStoredUser(null);
}
