// frontend/src/components/viewer/CrossModalToggle.tsx
import React from 'react';
import { Eye, Radio, Info } from 'lucide-react';
import { clsx } from 'clsx';
import { useAppStore } from '../../store/useAppStore';
import { Tooltip } from '../ui/Tooltip';

export const CrossModalToggle: React.FC = () => {
  const { crossModalActiveLayer, setCrossModalLayer } = useAppStore();

  return (
    <div className="flex items-center gap-2 p-1.5 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-800">
      <button
        onClick={() => setCrossModalLayer('optical')}
        className={clsx(
          'flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all',
          crossModalActiveLayer === 'optical'
            ? 'bg-sky-600 text-white shadow-md shadow-sky-950 border border-sky-400/40'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
        )}
      >
        <Eye className="w-3.5 h-3.5" />
        <span>OPTICAL (RGB/NIR)</span>
      </button>

      <button
        onClick={() => setCrossModalLayer('sar')}
        className={clsx(
          'flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all',
          crossModalActiveLayer === 'sar'
            ? 'bg-amber-600 text-white shadow-md shadow-amber-950 border border-amber-400/40'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
        )}
      >
        <Radio className="w-3.5 h-3.5" />
        <span>SAR RADAR (C-BAND)</span>
      </button>

      <Tooltip
        position="bottom"
        content="Optical imagery provides spectral/contextual information. SAR (Synthetic Aperture Radar) provides structural backscatter information through cloud cover. Cross-modal agreement regions (green) appear in both."
      >
        <div className="p-1 text-slate-400 hover:text-cyan-400 transition-colors cursor-help">
          <Info className="w-4 h-4" />
        </div>
      </Tooltip>
    </div>
  );
};
