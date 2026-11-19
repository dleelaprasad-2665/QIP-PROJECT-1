import React from 'react';
import {
  LayoutDashboard,
  ScanSearch,
  Crosshair,
  Boxes,
  History,
  BarChart3,
  FileText,
  Settings,
  LogOut,
  Building
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export type NavigationTab =
  | 'dashboard'
  | 'inspection'
  | 'defect-detection'
  | 'inventory'
  | 'history'
  | 'analytics'
  | 'reports'
  | 'evaluation'
  | 'settings';

interface SidebarProps {
  activeTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  const { user, logout } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'inspection', label: 'Material Inspection', icon: ScanSearch },
    { id: 'defect-detection', label: 'Defect Detection', icon: Crosshair },
    { id: 'inventory', label: 'Material Inventory', icon: Boxes },
    { id: 'history', label: 'Inspection History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none z-20">
      <div>
        {/* Enterprise Brand Header */}
        <div className="h-16 px-6 flex items-center gap-3 border-b border-gray-200">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
            <Building className="w-4 h-4 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm tracking-tight text-gray-900">
              Construct<span className="text-blue-600">IQ</span>
            </span>
            <span className="text-[10px] uppercase font-medium tracking-wider text-gray-500">
              Material Quality & Reuse
            </span>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="p-3 space-y-0.5">
          <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-gray-400">
            Navigation
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id as NavigationTab)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold border-l-2 border-blue-600 rounded-l-none'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer Profile & Logout */}
      <div className="p-4 border-t border-gray-200 space-y-2 bg-gray-50/50">
        <div className="px-2 py-1 text-xs">
          <div className="text-[11px] text-gray-500">Signed in as</div>
          <div className="text-gray-900 font-medium truncate">{user?.full_name || 'Inspector'}</div>
          <div className="text-[10px] text-blue-600 font-mono capitalize">{user?.role?.replace('_', ' ') || 'Site Engineer'}</div>
        </div>

        <button
          onClick={logout}
          className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs font-medium text-gray-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors border border-transparent hover:border-rose-200"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
