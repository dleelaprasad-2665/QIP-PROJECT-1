import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { RoleBadge } from '../common/Badge';
import { Building2, ShieldCheck, ChevronDown, Bell, LogIn, Search, CheckCircle } from 'lucide-react';

interface NavbarProps {
  currentSite: string;
  onSiteChange: (site: string) => void;
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentSite, onSiteChange, onOpenAuth }) => {
  const { user, switchRoleDemo } = useAuth();
  const [showRoleMenu, setShowRoleMenu] = useState(false);

  const sites = [
    'Central Yard A',
    'Skyline Tower Phase 2',
    'Metro Rail Extension Yard 4',
    'Harbor Logistic Hub',
    'EcoCity Residential Block B'
  ];

  return (
    <header className="h-16 border-b border-gray-200 bg-white px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Left: Site Selector & Quick Search */}
      <div className="flex items-center gap-4">
        {/* Site Location Selector */}
        <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-lg text-sm">
          <Building2 className="w-4 h-4 text-blue-600" />
          <span className="text-gray-500 text-xs font-medium">Site:</span>
          <select
            value={currentSite}
            onChange={(e) => onSiteChange(e.target.value)}
            aria-label="Active Construction Site"
            className="bg-transparent text-gray-800 text-xs font-semibold focus:outline-none cursor-pointer pr-1"
          >
            <option value="All">All Construction Sites</option>
            {sites.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* System Online Status */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-600" />
          <span>System Online • AI Core Ready</span>
        </div>
      </div>

      {/* Right Controls: Role Switcher, Alerts & Profile */}
      <div className="flex items-center gap-3">
        {/* Role Demo Switcher */}
        <div className="relative">
          <button
            onClick={() => setShowRoleMenu(!showRoleMenu)}
            className="flex items-center gap-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-700 transition-colors"
            title="Switch User Role Demonstration"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
            <RoleBadge role={user?.role || 'inspector'} />
            <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
          </button>

          {showRoleMenu && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-xl shadow-lg py-1.5 z-50">
              <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 border-b border-gray-100 mb-1">
                Simulate Role Access
              </div>
              <button
                onClick={() => { switchRoleDemo('admin'); setShowRoleMenu(false); }}
                className="w-full px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50 flex items-center justify-between"
              >
                <span className="font-medium">Administrator</span>
                <span className="text-[10px] text-orange-600 font-mono">Full Access</span>
              </button>
              <button
                onClick={() => { switchRoleDemo('site_engineer'); setShowRoleMenu(false); }}
                className="w-full px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50 flex items-center justify-between"
              >
                <span className="font-medium">Site Engineer</span>
                <span className="text-[10px] text-blue-600 font-mono">QA & Sign-off</span>
              </button>
              <button
                onClick={() => { switchRoleDemo('inspector'); setShowRoleMenu(false); }}
                className="w-full px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50 flex items-center justify-between"
              >
                <span className="font-medium">Field Inspector</span>
                <span className="text-[10px] text-gray-500 font-mono">Capture & Staging</span>
              </button>
            </div>
          )}
        </div>

        {/* User Card */}
        {user ? (
          <div className="flex items-center gap-2.5 pl-3 border-l border-gray-200">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-bold text-white text-xs">
              {user.full_name ? user.full_name.charAt(0) : 'U'}
            </div>
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-xs font-semibold text-gray-900 leading-tight truncate max-w-[140px]">{user.full_name}</span>
              <span className="text-[11px] text-gray-500 font-mono">@{user.username}</span>
            </div>
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors shadow-xs"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
};
