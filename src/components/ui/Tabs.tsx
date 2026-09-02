// frontend/src/components/ui/Tabs.tsx
import React from 'react';
import { clsx } from 'clsx';

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  count?: number;
}

interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
  variant?: 'pill' | 'underline';
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className,
  variant = 'pill',
}) => {
  return (
    <div className={clsx('flex items-center gap-1 p-1 rounded-lg bg-[#090909] border border-white/10 font-mono', className)}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={clsx(
              'flex items-center gap-2 px-3 py-1.5 text-xs uppercase tracking-wider font-semibold rounded transition-all cursor-pointer select-none',
              isActive
                ? 'bg-[#38BDF8] text-[#050505] shadow-md shadow-sky-500/20 font-bold'
                : 'text-[#A0A0A0] hover:text-white hover:bg-white/5'
            )}
          >
            {tab.icon}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                className={clsx(
                  'text-[10px] px-1.5 py-0.2 rounded font-mono',
                  isActive ? 'bg-[#050505] text-[#38BDF8]' : 'bg-[#1C1C1C] text-[#A0A0A0]'
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
