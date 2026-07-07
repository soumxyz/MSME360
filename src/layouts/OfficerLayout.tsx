import React from 'react';
import { Outlet, NavLink, Link } from 'react-router-dom';
import { 
  Activity, 
  LayoutDashboard, 
  ShieldAlert, 
  FileCheck, 
  PieChart, 
  Settings, 
  Search, 
  Bell, 
  Users
} from 'lucide-react';

const Sidebar = () => (
  <aside className="w-64 bg-primary border-r border-primary-hover hidden lg:flex flex-col h-screen fixed left-0 top-0">
    <div className="h-16 flex items-center px-6 border-b border-primary-hover">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-8 h-8 bg-white rounded flex items-center justify-center">
          <Activity className="w-5 h-5 text-primary" />
        </div>
        <span className="font-semibold text-lg text-white tracking-tight">IDBI Officer Hub</span>
      </Link>
    </div>
    
    <div className="flex-grow py-6 px-4 flex flex-col gap-1">
      <NavItem to="/officer/dashboard" icon={<LayoutDashboard className="w-4 h-4" />} label="Dashboard" />
      <NavItem to="/officer/applications" icon={<FileCheck className="w-4 h-4" />} label="Applications" />
      <NavItem to="/officer/businesses" icon={<Users className="w-4 h-4" />} label="Businesses" />
      <NavItem to="/officer/risk-queue" icon={<ShieldAlert className="w-4 h-4" />} label="Risk Queue" />
      <NavItem to="/officer/health-cards" icon={<Activity className="w-4 h-4" />} label="Financial Health Cards" />
      <NavItem to="/officer/reports" icon={<PieChart className="w-4 h-4" />} label="Reports" />
    </div>

    <div className="p-4 border-t border-primary-hover">
      <NavItem to="/officer/settings" icon={<Settings className="w-4 h-4" />} label="Settings" />
    </div>
  </aside>
);

const NavItem = ({ to, icon, label }: { to: string, icon: React.ReactNode, label: string }) => (
  <NavLink 
    to={to} 
    className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-colors ${
      isActive 
        ? 'bg-white/20 text-white' 
        : 'text-white/70 hover:bg-white/10 hover:text-white'
    }`}
  >
    {icon}
    {label}
  </NavLink>
);

const Topbar = () => (
  <header className="h-16 bg-white border-b border-border flex items-center justify-between px-6 sticky top-0 z-40">
    <div className="flex items-center gap-4">
      <h2 className="text-lg font-semibold text-text-primary">Underwriting Dashboard</h2>
    </div>
    
    <div className="flex items-center gap-5">
      <div className="relative hidden md:block">
        <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          type="text" 
          placeholder="Search Application ID or Business..." 
          className="pl-9 pr-4 py-1.5 bg-background-muted border-none rounded text-sm focus:outline-none focus:ring-1 focus:ring-primary w-80"
        />
      </div>
      <button className="text-text-secondary hover:text-text-primary relative">
        <Bell className="w-5 h-5" />
        <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full border border-white"></span>
      </button>
      <div className="flex items-center gap-2 border-l border-border pl-4">
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm border border-primary/20 cursor-pointer">
          RK
        </div>
        <div className="hidden md:block">
          <p className="text-xs font-semibold text-text-primary">Rajesh Kumar</p>
          <p className="text-[10px] text-text-secondary">Senior Loan Officer</p>
        </div>
      </div>
    </div>
  </header>
);

export default function OfficerLayout() {
  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary selection:text-white flex">
      <Sidebar />
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen overflow-x-hidden">
        <Topbar />
        <Outlet />
      </div>
    </div>
  );
}
