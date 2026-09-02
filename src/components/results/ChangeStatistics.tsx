// frontend/src/components/results/ChangeStatistics.tsx
import React from 'react';
import { Activity, TrendingUp, TrendingDown } from 'lucide-react';

interface ChangeStatisticsProps {
  stats: Record<string, any> | null;
}

export const ChangeStatistics: React.FC<ChangeStatisticsProps> = ({ stats }) => {
  if (!stats || Object.keys(stats).length === 0) return null;

  return (
    <div className="p-3.5 rounded-lg bg-[#050505] border border-white/10 space-y-2.5 font-mono">
      <div className="flex items-center justify-between pb-1.5 border-b border-white/10">
        <span className="text-[10px] font-bold text-[#38BDF8] uppercase tracking-wider flex items-center gap-1.5">
          <Activity className="w-3 h-3" />
          <span>CHANGE STATISTICS</span>
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {Object.entries(stats).map(([key, val]) => {
          const strVal = String(val);
          const isBuiltUp = key.toLowerCase().includes('built') || key.toLowerCase().includes('inundat');
          const isNegative = strVal.startsWith('-');
          const isPositive = strVal.startsWith('+');

          return (
            <div key={key} className="p-2 rounded bg-[#0D0D0D] border border-white/10">
              <div className="text-[9px] text-[#A0A0A0] uppercase truncate">
                {key.replace(/_/g, ' ')}
              </div>
              <div className="text-xs font-bold mt-0.5 flex items-center gap-1">
                {isPositive && <TrendingUp className="w-3 h-3 text-[#38BDF8]" />}
                {isNegative && <TrendingDown className="w-3 h-3 text-[#EF4444]" />}
                <span
                  className={
                    isBuiltUp || isPositive
                      ? 'text-[#38BDF8]'
                      : isNegative
                      ? 'text-[#EF4444]'
                      : 'text-white'
                  }
                >
                  {typeof val === 'number' && key.includes('fraction')
                    ? `${(val * 100).toFixed(1)}%`
                    : strVal}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
