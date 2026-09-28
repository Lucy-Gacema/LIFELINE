const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function getToken() {
  return localStorage.getItem("lifeline_token");
}

export function setToken(token) {
  if (token) localStorage.setItem("lifeline_token", token);
  else localStorage.removeItem("lifeline_token");
}

export function getStoredUser() {
  const raw = localStorage.getItem("lifeline_user");
  return raw ? JSON.parse(raw) : null;
}

export function setStoredUser(user) {
  if (user) localStorage.setItem("lifeline_user", JSON.stringify(user));
  else localStorage.removeItem("lifeline_user");
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}


export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (err) {
    throw new ApiError("Could not reach the server. Check your connection.", 0);
  }

  if (response.status === 401) {
    setToken(null);
    setStoredUser(null);
    window.location.href = "/login";
    throw new ApiError("Your session expired. Please log in again.", 401);
  }

  if (!response.ok) {
    let detail = "Something went wrong. Please try again.";
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
     
    }
    throw new ApiError(typeof detail === "string" ? detail : JSON.stringify(detail), response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}

export { API_BASE_URL };
