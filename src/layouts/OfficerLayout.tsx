import React, { useEffect, useState } from 'react';
import { Outlet, NavLink, Link, useLocation, useNavigate } from 'react-router-dom';
import { logout } from '../lib/api';
import {
  Activity,
  LayoutDashboard,
  ShieldAlert,
  FileCheck,
  PieChart,
  Settings,
  Search,
  Menu,
  X,
  Users,
  LogOut,
  ChevronDown
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/officer/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/officer/applications', icon: FileCheck, label: 'Applications' },
  { to: '/officer/businesses', icon: Users, label: 'Businesses' },
  { to: '/officer/risk-queue', icon: ShieldAlert, label: 'Risk Queue' },
  { to: '/officer/health-cards', icon: Activity, label: 'Financial Health Cards' },
  { to: '/officer/reports', icon: PieChart, label: 'Reports' },
];

const PAGE_TITLES: [string, string][] = [
  ['/officer/dashboard', 'Underwriting Dashboard'],
  ['/officer/applications/', 'Underwriting Review'],
  ['/officer/applications', 'Applications Queue'],
  ['/officer/businesses', 'Business Directory'],
  ['/officer/risk-queue', 'Risk Queue'],
  ['/officer/health-cards', 'Financial Health Cards'],
  ['/officer/reports', 'Reports'],
  ['/officer/settings', 'Settings'],
];

const NavItem = ({ to, icon: Icon, label, onNavigate }: { to: string, icon: React.ElementType, label: string, onNavigate?: () => void }) => (
  <NavLink
    to={to}
    onClick={onNavigate}
    className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-colors ${
      isActive
        ? 'bg-white/20 text-white'
        : 'text-white/70 hover:bg-white/10 hover:text-white'
    }`}
  >
    <Icon className="w-4 h-4" aria-hidden="true" />
    {label}
  </NavLink>
);

const SidebarContent = ({ onNavigate }: { onNavigate?: () => void }) => (
  <>
    <div className="h-16 flex items-center px-6 border-b border-primary-hover shrink-0 bg-gradient-to-r from-primary to-primary-hover">
      <Link to="/" className="flex items-center gap-2" onClick={onNavigate}>
        <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center shadow-md">
          <Activity className="w-5 h-5 text-primary" aria-hidden="true" />
        </div>
        <div>
          <span className="font-bold text-base text-white tracking-tight block">IDBI Bank</span>
          <span className="text-[10px] text-white/80 tracking-wide">Credit Officer Portal</span>
        </div>
      </Link>
    </div>

    <div className="flex-grow py-6 px-4 flex flex-col gap-1 overflow-y-auto">
      {NAV_ITEMS.map((item) => (
        <NavItem key={item.to} to={item.to} icon={item.icon} label={item.label} onNavigate={onNavigate} />
      ))}
    </div>

    <div className="p-4 border-t border-primary-hover shrink-0 bg-primary/20">
      <NavItem to="/officer/settings" icon={Settings} label="Settings" onNavigate={onNavigate} />
      <div className="mt-3 px-3 py-2 bg-white/10 rounded text-xs text-white/70">
        <p className="font-medium text-white/90 mb-1">System Status</p>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
          <span>All Systems Operational</span>
        </div>
      </div>
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
        className="absolute left-0 top-0 h-full w-64 bg-primary flex flex-col shadow-2xl"
      >
        <button
          onClick={onClose}
          aria-label="Close navigation menu"
          className="absolute top-4 right-3 p-1.5 rounded text-white/80 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
        <SidebarContent onNavigate={onClose} />
      </aside>
    </div>
  );
};

const Topbar = ({ onMenuOpen }: { onMenuOpen: () => void }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);

  const title = PAGE_TITLES.find(([prefix]) => location.pathname.startsWith(prefix))?.[1] ?? 'Officer Hub';

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!showUserMenu) return;
    const handleClick = () => setShowUserMenu(false);
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [showUserMenu]);

  const submitSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    navigate(q ? `/officer/dashboard?q=${encodeURIComponent(q)}` : '/officer/dashboard');
  };

  const handleSignOut = () => {
    // Actual auth-token clear + navigate. Previously removed a non-existent key.
    logout();
    sessionStorage.clear();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-white border-b border-border flex items-center justify-between px-4 sm:px-6 sticky top-0 z-40 shadow-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuOpen}
          aria-label="Open navigation menu"
          className="lg:hidden p-2 -ml-1 rounded text-text-secondary hover:text-text-primary hover:bg-background-muted transition-colors"
        >
          <Menu className="w-5 h-5" aria-hidden="true" />
        </button>
        <h2 className="text-lg font-semibold text-text-primary truncate">{title}</h2>
      </div>

      <div className="flex items-center gap-5">
        <form onSubmit={submitSearch} className="relative hidden md:block" role="search">
          <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search application ID or business, press Enter to filter the queue"
            placeholder="Search Application ID or Business..."
            className="pl-9 pr-4 py-1.5 bg-background-muted border-none rounded text-sm focus:outline-none focus:ring-1 focus:ring-primary w-80"
          />
        </form>
        <div className="relative flex items-center gap-2 border-l border-border pl-4">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowUserMenu(!showUserMenu);
            }}
            className="flex items-center gap-2 hover:bg-background-muted px-2 py-1 rounded transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm border border-primary/20" aria-hidden="true">
              RK
            </div>
            <div className="hidden md:block text-left">
              <p className="text-xs font-semibold text-text-primary">Rajesh Kumar</p>
              <p className="text-[10px] text-text-secondary">Senior Loan Officer</p>
            </div>
            <ChevronDown className="w-4 h-4 text-text-secondary" />
          </button>
          
          {showUserMenu && (
            <div className="absolute right-0 top-12 w-48 bg-white border border-border rounded-lg shadow-lg py-2 z-50">
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
      </div>
    </header>
  );
};

export default function OfficerLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary selection:text-white flex">
      <aside className="w-64 bg-primary border-r border-primary-hover hidden lg:flex flex-col h-screen fixed left-0 top-0 shadow-xl">
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
