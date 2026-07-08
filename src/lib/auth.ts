/**
 * Minimal auth store: token + user role live in localStorage. Every API call
 * in `lib/api` reads `getAuthHeaders()` to attach `Authorization: Bearer …`.
 *
 * Storing JWT in localStorage instead of httpOnly cookies is a known trade-off
 * for a SPA without a matching server-side session; for a production deployment
 * we would move to same-origin cookies + CSRF tokens. Called out in the review.
 */
export type Role = "customer" | "officer";

export interface AuthState {
  token: string;
  role: Role;
  username: string;
  expiresAt: string;
}

const KEY = "msme360.auth";

const listeners = new Set<() => void>();

export function getAuth(): AuthState | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthState;
    if (Date.parse(parsed.expiresAt) <= Date.now()) {
      localStorage.removeItem(KEY);
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function setAuth(state: AuthState): void {
  localStorage.setItem(KEY, JSON.stringify(state));
  listeners.forEach((fn) => fn());
}

export function clearAuth(): void {
  localStorage.removeItem(KEY);
  listeners.forEach((fn) => fn());
}

export function getAuthHeaders(): Record<string, string> {
  const a = getAuth();
  return a ? { Authorization: `Bearer ${a.token}` } : {};
}

export function subscribe(fn: () => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}
