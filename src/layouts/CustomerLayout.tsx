import React, { useEffect, useState } from 'react';
import { Outlet, NavLink, Link, useNavigate } from 'react-router-dom';
import {
  Activity,
  LayoutDashboard,
  FileCheck,
  PieChart,
  Settings,
  Building2,
  Lightbulb,
  Files,
  Menu,
  X,
  LogOut,
  ChevronDown
} from 'lucide-react';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID } from '../lib/customer';

const NAV_ITEMS = [
  { to: '/customer/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/customer/insights', icon: Lightbulb, label: 'Business Insights' },
  { to: '/customer/loans', icon: FileCheck, label: 'Loan Offers' },
  { to: '/customer/applications', icon: Files, label: 'Applications' },
  { to: '/customer/reports', icon: PieChart, label: 'Reports' },
];

const NavItem = ({ to, icon: Icon, label, onNavigate }: { to: string, icon: React.ElementType, label: string, onNavigate?: () => void }) => (
  <NavLink
    to={to}
    onClick={onNavigate}
    className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-colors ${
      isActive
        ? 'bg-primary/5 text-primary'
        : 'text-text-secondary hover:bg-background-muted hover:text-text-primary'
    }`}
  >
    <Icon className="w-4 h-4" aria-hidden="true" />
    {label}
  </NavLink>
);

const SidebarContent = ({ onNavigate }: { onNavigate?: () => void }) => (
  <>
    <div className="h-16 flex items-center px-6 border-b border-border shrink-0">
      <Link to="/" className="flex items-center gap-2" onClick={onNavigate}>
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
          <Activity className="w-5 h-5 text-white" aria-hidden="true" />
        </div>
        <span className="font-semibold text-lg text-primary tracking-tight">CreditPulse AI</span>
      </Link>
    </div>

    <div className="flex-grow py-6 px-4 flex flex-col gap-1 overflow-y-auto">
      {NAV_ITEMS.map((item) => (
        <NavItem key={item.to} to={item.to} icon={item.icon} label={item.label} onNavigate={onNavigate} />
      ))}
    </div>

    <div className="p-4 border-t border-border shrink-0">
      <NavItem to="/customer/settings" icon={Settings} label="Settings" onNavigate={onNavigate} />
    </div>
  </>
);

const MobileDrawer = ({ open, onClose }: { open: boolean, onClose: () => void }) => {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
        className="absolute left-0 top-0 h-full w-64 bg-white flex flex-col shadow-2xl"
      >
        <button
          onClick={onClose}
          aria-label="Close navigation menu"
          className="absolute top-4 right-3 p-1.5 rounded text-text-secondary hover:text-text-primary hover:bg-background-muted transition-colors"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
        <SidebarContent onNavigate={onClose} />
      </aside>
    </div>
  );
};

const Topbar = ({ onMenuOpen }: { onMenuOpen: () => void }) => {
  const { data } = useBusinessDetail(DEMO_BUSINESS_ID);
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const businessName = data?.profile.name ?? 'Loading…';
  const initials = data?.profile.name.split(' ').map((w) => w[0]).slice(0, 2).join('') ?? '··';

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!showUserMenu) return;
    const handleClick = () => setShowUserMenu(false);
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [showUserMenu]);

  const handleSignOut = () => {
    // Clear any stored session data
    localStorage.removeItem('user');
    sessionStorage.clear();
    // Navigate to login
    navigate('/login');
  };

  return (
    <header className="h-16 bg-white border-b border-border flex items-center justify-between px-4 sm:px-6 sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuOpen}
          aria-label="Open navigation menu"
          className="lg:hidden p-2 -ml-1 rounded text-text-secondary hover:text-text-primary hover:bg-background-muted transition-colors"
        >
          <Menu className="w-5 h-5" aria-hidden="true" />
        </button>
        {/* Active business context (single-business demo account) */}
        <div className="flex items-center gap-2 px-3 py-1.5 border border-border rounded">
          <Building2 className="w-4 h-4 text-text-secondary" aria-hidden="true" />
          <span className="text-sm font-medium text-text-primary">{businessName}</span>
        </div>
      </div>

      <div className="relative flex items-center gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowUserMenu(!showUserMenu);
          }}
          className="flex items-center gap-2 hover:bg-background-muted px-2 py-1 rounded transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm border border-primary/20" aria-hidden="true">
            {initials}
          </div>
          <ChevronDown className="w-4 h-4 text-text-secondary hidden md:block" />
        </button>
        
        {showUserMenu && (
          <div className="absolute right-0 top-12 w-48 bg-white border border-border rounded-lg shadow-lg py-2 z-50">
            <div className="px-4 py-2 border-b border-border">
              <p className="text-xs font-semibold text-text-primary">{businessName}</p>
            </div>
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-text-primary hover:bg-background-muted transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default function CustomerLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary selection:text-white flex">
      <aside className="w-64 bg-white border-r border-border hidden lg:flex flex-col h-screen fixed left-0 top-0">
        <SidebarContent />
      </aside>
      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen overflow-x-hidden">
        <Topbar onMenuOpen={() => setDrawerOpen(true)} />
        <Outlet />
      </div>
    </div>
  );
}
