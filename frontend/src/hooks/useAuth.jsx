import React, { createContext, useContext, useEffect, useState } from "react";
import { getStoredUser, setStoredUser, getToken } from "../api/client.js";
import * as authApi from "../api/auth.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    
    const onStorage = () => setUser(getStoredUser());
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const loginWithPassword = async (email, password) => {
    setLoading(true);
    try {
      const u = await authApi.loginWithPassword(email, password);
      setUser(u);
      return u;
    } finally {
      setLoading(false);
    }
  };

  const loginWithPin = async (userId, pin) => {
    setLoading(true);
    try {
      const u = await authApi.loginWithPin(userId, pin);
      setUser(u);
      return u;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
  };

  const hasPermission = (permission) => !!user?.permissions?.includes(permission);

  return (
    <AuthContext.Provider value={{ user, loading, loginWithPassword, loginWithPin, logout, hasPermission, isAuthenticated: !!user && !!getToken() }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
