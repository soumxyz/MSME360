import React from 'react';
import { Outlet, NavLink, Link } from 'react-router-dom';
import { 
  Activity, 
  LayoutDashboard, 
  FileCheck, 
  PieChart, 
  Settings, 
  Search, 
  Bell, 
  Building2, 
  ChevronDown,
  Lightbulb,
  Files
} from 'lucide-react';

const Sidebar = () => (
  <aside className="w-64 bg-white border-r border-border hidden lg:flex flex-col h-screen fixed left-0 top-0">
    <div className="h-16 flex items-center px-6 border-b border-border">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <span className="font-semibold text-lg text-primary tracking-tight">CreditPulse AI</span>
      </Link>
    </div>
    
    <div className="flex-grow py-6 px-4 flex flex-col gap-1">
      <NavItem to="/customer/dashboard" icon={<LayoutDashboard className="w-4 h-4" />} label="Dashboard" />
      <NavItem to="/customer/insights" icon={<Lightbulb className="w-4 h-4" />} label="Business Insights" />
      <NavItem to="/customer/loans" icon={<FileCheck className="w-4 h-4" />} label="Loan Offers" />
      <NavItem to="/customer/applications" icon={<Files className="w-4 h-4" />} label="Applications" />
      <NavItem to="/customer/reports" icon={<PieChart className="w-4 h-4" />} label="Reports" />
    </div>

    <div className="p-4 border-t border-border">
      <NavItem to="/customer/settings" icon={<Settings className="w-4 h-4" />} label="Settings" />
    </div>
  </aside>
);

const NavItem = ({ to, icon, label }: { to: string, icon: React.ReactNode, label: string }) => (
  <NavLink 
    to={to} 
    className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-colors ${
      isActive 
        ? 'bg-primary/5 text-primary' 
        : 'text-text-secondary hover:bg-background-muted hover:text-text-primary'
    }`}
  >
    {icon}
    {label}
  </NavLink>
);

const Topbar = () => (
  <header className="h-16 bg-white border-b border-border flex items-center justify-between px-6 sticky top-0 z-40">
    <div className="flex items-center gap-4">
      {/* Business Switcher */}
      <div className="flex items-center gap-2 px-3 py-1.5 border border-border rounded cursor-pointer hover:bg-background-muted transition-colors">
        <Building2 className="w-4 h-4 text-text-secondary" />
        <span className="text-sm font-medium text-text-primary">Acme Industries Pvt Ltd</span>
        <ChevronDown className="w-4 h-4 text-text-secondary ml-2" />
      </div>
    </div>
    
    <div className="flex items-center gap-5">
      <div className="relative hidden md:block">
        <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          type="text" 
          placeholder="Search..." 
          className="pl-9 pr-4 py-1.5 bg-background-muted border-none rounded text-sm focus:outline-none focus:ring-1 focus:ring-primary w-64"
        />
      </div>
      <button className="text-text-secondary hover:text-text-primary relative">
        <Bell className="w-5 h-5" />
        <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full border border-white"></span>
      </button>
      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm border border-primary/20 cursor-pointer">
        RK
      </div>
    </div>
  </header>
);

export default function CustomerLayout() {
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
