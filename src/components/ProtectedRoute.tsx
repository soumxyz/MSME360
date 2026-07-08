import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { getAuth, type Role } from '../lib/auth';

/**
 * Client-side guard for `/customer/*` and `/officer/*` route trees. Note that
 * the *authoritative* check is server-side: every officer endpoint uses
 * `Depends(require_officer)`, so a bypass of this component still hits a 403.
 * This exists so URL-bar navigation doesn't render officer chrome to logged-out
 * users, not as the security boundary itself.
 */
export default function ProtectedRoute({ role }: { role: Role }) {
  const auth = getAuth();
  const location = useLocation();

  if (!auth) {
    // Preserve where they were trying to go so we can bounce them back after login.
    return <Navigate to={`/login?role=${role}&next=${encodeURIComponent(location.pathname)}`} replace />;
  }
  if (auth.role !== role) {
    // Signed in as the wrong role — send them to their own dashboard rather
    // than to the login screen.
    const dest = auth.role === 'officer' ? '/officer/dashboard' : '/customer/dashboard';
    return <Navigate to={dest} replace />;
  }
  return <Outlet />;
}
