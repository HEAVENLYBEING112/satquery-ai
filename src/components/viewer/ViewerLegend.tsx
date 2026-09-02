// frontend/src/components/viewer/ViewerLegend.tsx
import React from 'react';
import { Layers } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { clsx } from 'clsx';

export const ViewerLegend: React.FC = () => {
  const { viewerLayer, setViewerLayer } = useAppStore();

  const layers: Array<{ id: typeof viewerLayer; label: string }> = [
    { id: 'original', label: 'ORIGINAL' },
    { id: 'evidence', label: 'AI EVIDENCE' },
    { id: 'change_mask', label: 'CHANGE MAP' },
    { id: 'segmentation', label: 'SEGMENTATION' },
    { id: 'grounding', label: 'GROUNDING' },
  ];

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 p-2 rounded-lg bg-[#050505] border border-white/10 text-xs font-mono">
      {/* Layer selector */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold text-[#A0A0A0] uppercase mr-1">DATA LAYERS:</span>
        <div className="flex flex-wrap items-center gap-1">
          {layers.map((l) => {
            const isActive = viewerLayer === l.id;
            return (
              <button
                key={l.id}
                onClick={() => setViewerLayer(l.id)}
                className={clsx(
                  'px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider transition-colors cursor-pointer',
                  isActive
                    ? 'bg-[#38BDF8] text-[#050505] shadow-sm font-black'
                    : 'text-[#A0A0A0] hover:text-white bg-[#111111] border border-white/10 hover:border-white/20'
                )}
              >
                {isActive ? '◉' : '○'} {l.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Target Color Indicators */}
      <div className="flex items-center gap-3 text-[10px] text-[#A0A0A0]">
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-xs bg-[#38BDF8]" />
          <span>WATER</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-xs bg-[#22C55E]" />
          <span>CONSENSUS</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-xs bg-[#EF4444]" />
          <span>CHANGE</span>
        </div>
      </div>
    </div>
  );
};
