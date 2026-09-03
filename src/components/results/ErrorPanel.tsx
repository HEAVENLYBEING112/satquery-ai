// frontend/src/components/results/ErrorPanel.tsx
import React from 'react';
import { EngineError } from '../../types/engine';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { Button } from '../ui/Button';

interface ErrorPanelProps {
  errors: EngineError[];
  onRetry: () => void;
}

export const ErrorPanel: React.FC<ErrorPanelProps> = ({ errors, onRetry }) => {
  if (!errors || errors.length === 0) return null;

  return (
    <div
      role="alert"
      className="p-5 rounded-xl bg-[#111111] border border-[#EF4444]/40 text-[#EF4444] space-y-3 shadow-2xl font-mono"
    >
      <div className="flex items-center gap-2">
        <AlertCircle className="w-5 h-5 text-[#EF4444] shrink-0" />
        <h4 className="font-bold text-[#EF4444] text-xs uppercase tracking-wider">
          ⚠ SATELLITE ENGINE WORKFLOW FAILED
        </h4>
      </div>

      <div className="space-y-2">
        {errors.map((err, idx) => (
          <div key={idx} className="p-3 rounded-lg bg-[#050505] border border-[#EF4444]/20 space-y-1">
            <div className="text-[11px] font-bold text-[#EF4444]">
              FAULT CODE: {err.code}
            </div>
            <p className="text-xs text-[#A0A0A0] leading-relaxed font-sans">{err.message}</p>
          </div>
        ))}
      </div>

      <div className="pt-2 flex justify-end">
        <Button size="sm" variant="danger" onClick={onRetry} icon={<RotateCcw className="w-3.5 h-3.5" />}>
          RETRY
        </Button>
      </div>
    </div>
  );
};
