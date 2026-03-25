import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// ─────────────────────────────────────────────
// CONFIG — change these to match your Django URLs
// ─────────────────────────────────────────────
const API_BASE = 'http://localhost:8000';         // your Django dev server
const ENDPOINTS = {
  login: `${API_BASE}/api/token/`,                // simplejwt default
  refresh: `${API_BASE}/api/token/refresh/`,      // simplejwt default
  register: `${API_BASE}/api/auth/register/`,     // your register view URL — update if different
  me: `${API_BASE}/api/auth/me/`,                 // your user-detail view URL — update if different
};

// How many minutes before access token expires should we proactively refresh?
const REFRESH_BUFFER_MINUTES = 1;

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
};

const getStoredTokens = () => ({
  access: localStorage.getItem('access_token'),
  refresh: localStorage.getItem('refresh_token'),
});

const storeTokens = (access, refresh) => {
  localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
};

const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

const isTokenExpired = (token) => {
  const payload = parseJwt(token);
  if (!payload?.exp) return true;
  const expiresInMs = payload.exp * 1000 - Date.now();
  return expiresInMs < REFRESH_BUFFER_MINUTES * 60 * 1000;
};

// ─────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true); // true on mount while we check stored tokens
  const [error, setError]     = useState(null);

  // ── Fetch the logged-in user's profile ──
  const fetchUser = useCallback(async (accessToken) => {
    const res = await fetch(ENDPOINTS.me, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!res.ok) throw new Error('Could not fetch user profile.');
    return await res.json();
  }, []);

  // ── Silently refresh the access token ──
  const refreshAccessToken = useCallback(async () => {
    const { refresh } = getStoredTokens();
    if (!refresh) throw new Error('No refresh token.');

    const res = await fetch(ENDPOINTS.refresh, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (!res.ok) throw new Error('Session expired. Please log in again.');

    const data = await res.json();
    storeTokens(data.access, data.refresh ?? null);
    return data.access;
  }, []);

  // ── Get a valid access token (refresh if needed) ──
  const getValidAccessToken = useCallback(async () => {
    let { access } = getStoredTokens();
    if (!access) throw new Error('Not authenticated.');
    if (isTokenExpired(access)) {
      access = await refreshAccessToken();
    }
    return access;
  }, [refreshAccessToken]);

  // ── On mount: restore session from localStorage ──
  useEffect(() => {
    const restoreSession = async () => {
      const { access, refresh } = getStoredTokens();
      if (!access || !refresh) {
        setLoading(false);
        return;
      }
      try {
        const validToken = isTokenExpired(access)
          ? await refreshAccessToken()
          : access;
        const userData = await fetchUser(validToken);
        setUser(userData);
      } catch {
        clearTokens();
      } finally {
        setLoading(false);
      }
    };

    restoreSession();
  }, [fetchUser, refreshAccessToken]);

  // ── Proactive token refresh timer ──
  useEffect(() => {
    if (!user) return;

    const scheduleRefresh = () => {
      const { access } = getStoredTokens();
      if (!access) return;
      const payload = parseJwt(access);
      if (!payload?.exp) return;

      const msUntilRefresh =
        payload.exp * 1000 - Date.now() - REFRESH_BUFFER_MINUTES * 60 * 1000;

      if (msUntilRefresh <= 0) return;

      return setTimeout(async () => {
        try {
          await refreshAccessToken();
          scheduleRefresh();
        } catch {
          logout();
        }
      }, msUntilRefresh);
    };

    const timer = scheduleRefresh();
    return () => clearTimeout(timer);
  }, [user, refreshAccessToken]);

  // ── Login ──
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(ENDPOINTS.login, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.detail ?? 'Invalid credentials.');
      }

      const { access, refresh } = await res.json();
      storeTokens(access, refresh);

      const userData = await fetchUser(access);
      setUser(userData);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ── Signup ──
  const signup = async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(ENDPOINTS.register, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const message =
          data?.username?.[0] ?? data?.email?.[0] ?? data?.password?.[0] ?? 'Signup failed.';
        throw new Error(message);
      }

      // Auto-login after successful registration
      await login(username, password);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ── Logout ──
  const logout = () => {
    clearTokens();
    setUser(null);
    setError(null);
    // Optional: call a Django logout / token-blacklist endpoint here
    // fetch(ENDPOINTS.logout, { method: 'POST', ... });
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, signup, logout, getValidAccessToken }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// ─────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};