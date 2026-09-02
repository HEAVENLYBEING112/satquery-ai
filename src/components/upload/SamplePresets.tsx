// frontend/src/components/upload/SamplePresets.tsx
import React from 'react';
import { SAMPLE_DATASETS } from '../../api/mock/mockData';
import { useAppStore } from '../../store/useAppStore';
import { Database } from 'lucide-react';
import { clsx } from 'clsx';

export const SamplePresets: React.FC = () => {
  const { activePresetId, loadPreset } = useAppStore();

  return (
    <div className="space-y-2 font-mono">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#A0A0A0] flex items-center gap-1.5">
          <Database className="w-3 h-3 text-[#38BDF8]" />
          <span>BENCHMARK DATASETS</span>
        </span>
      </div>

      <div className="space-y-1.5">
        {SAMPLE_DATASETS.map((dataset) => {
          const isSelected = activePresetId === dataset.id;
          return (
            <button
              key={dataset.id}
              onClick={() => loadPreset(dataset)}
              className={clsx(
                'w-full text-left p-2.5 rounded-lg border transition-all cursor-pointer flex flex-col gap-0.5',
                isSelected
                  ? 'bg-[#161616] border-[#38BDF8] shadow-md'
                  : 'bg-[#111111] border-white/10 hover:border-white/20'
              )}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-white truncate">{dataset.title}</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-[#050505] text-[#38BDF8] border border-sky-400/30">
                  {dataset.badge.split(' ')[0]}
                </span>
              </div>
              <p className="text-[10px] text-[#A0A0A0] truncate">{dataset.subtitle}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
