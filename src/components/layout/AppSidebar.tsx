// frontend/src/components/layout/AppSidebar.tsx
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Terminal,
  Scan,
  GitCompare,
  Layers,
  Cpu,
  History,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  User,
} from 'lucide-react';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'DASHBOARD', icon: <LayoutDashboard className="w-4 h-4" /> },
  { path: '/workspace', label: 'AI WORKSPACE', icon: <Terminal className="w-4 h-4" />, highlight: true },
  { path: '/single-image', label: 'SINGLE IMAGE', icon: <Scan className="w-4 h-4" /> },
  { path: '/change-detection', label: 'CHANGE DETECTION', icon: <GitCompare className="w-4 h-4" /> },
  { path: '/optical-sar', label: 'OPTICAL + SAR', icon: <Layers className="w-4 h-4" /> },
  { path: '/agent-monitor', label: 'AGENT MONITOR', icon: <Cpu className="w-4 h-4" /> },
  { path: '/history', label: 'ANALYSIS HISTORY', icon: <History className="w-4 h-4" /> },
  { path: '/reports', label: 'REPORTS', icon: <FileText className="w-4 h-4" /> },
  { path: '/settings', label: 'SETTINGS', icon: <Settings className="w-4 h-4" /> },
];

export const AppSidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={clsx(
        'border-r border-white/10 bg-[#090909] transition-all duration-200 flex flex-col justify-between shrink-0 select-none z-20 font-mono',
        collapsed ? 'w-16' : 'w-56'
      )}
    >
      <div className="p-2.5">
        {/* Collapse toggle button */}
        <div className="flex items-center justify-between pb-2.5 mb-2 border-b border-white/10">
          {!collapsed && (
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#666666]">
              COMMAND SYSTEM
            </span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded text-[#A0A0A0] hover:text-white hover:bg-white/5 ml-auto transition-colors cursor-pointer"
            title={collapsed ? 'Expand Navigation' : 'Collapse Navigation'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4 text-[#38BDF8]" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Nav links */}
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-2.5 px-3 py-2 rounded text-xs font-semibold tracking-wider transition-all group',
                  isActive
                    ? 'bg-sky-950/40 text-[#38BDF8] border-l-2 border-[#38BDF8] rounded-l-none font-bold'
                    : 'text-[#A0A0A0] hover:text-white hover:bg-white/5'
                )
              }
              title={collapsed ? item.label : undefined}
            >
              <div className="shrink-0 group-hover:text-[#38BDF8] transition-colors">{item.icon}</div>
              {!collapsed && <span className="truncate">{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* User / Station Badge */}
      <div className="p-2.5 border-t border-white/10">
        <div className={clsx('flex items-center gap-2.5 p-2 rounded-lg bg-[#111111] border border-white/10', collapsed && 'justify-center')}>
          <div className="w-7 h-7 rounded bg-[#1C1C1C] border border-sky-400/30 flex items-center justify-center text-[#38BDF8] shrink-0">
            <User className="w-3.5 h-3.5" />
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <p className="text-[11px] font-bold text-white truncate">ISRO COMMAND</p>
              <p className="text-[9px] text-[#38BDF8] uppercase tracking-wider truncate">Operator Online</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
