// frontend/src/components/chat/ProcessingSteps.tsx
import React, { useState, useEffect } from 'react';
import { CheckCircle2, Loader2, Radio } from 'lucide-react';
import { clsx } from 'clsx';

interface ProcessingStepsProps {
  currentStatusText?: string;
}

const STEPS = [
  'QUERY RECEIVED',
  'INPUT VALIDATED',
  'SELECTING SPECIALIST WORKFLOW',
  'EXECUTING ANALYSIS',
  'GENERATING EVIDENCE',
  'PREPARING RESPONSE',
];

export const ProcessingSteps: React.FC<ProcessingStepsProps> = ({ currentStatusText }) => {
  const [activeStepIndex, setActiveStepIndex] = useState(2);

  useEffect(() => {
    const timer1 = setTimeout(() => setActiveStepIndex(3), 400);
    const timer2 = setTimeout(() => setActiveStepIndex(4), 800);
    const timer3 = setTimeout(() => setActiveStepIndex(5), 1100);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="p-3.5 rounded-lg bg-[#050505] border border-sky-400/30 space-y-2.5 font-mono text-xs shadow-2xl">
      <div className="flex items-center justify-between pb-1.5 border-b border-white/10">
        <span className="text-[#38BDF8] font-bold flex items-center gap-2 text-[11px] uppercase tracking-wider">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-[#38BDF8]" />
          <span>SATQUERY AI PROCESSING</span>
        </span>
        <span className="text-[9px] text-[#22C55E] uppercase font-bold">TELEMETRY ACTIVE</span>
      </div>

      <div className="space-y-1.5">
        {STEPS.map((label, index) => {
          const isDone = index < activeStepIndex;
          const isCurrent = index === activeStepIndex;

          return (
            <div
              key={index}
              className={clsx(
                'flex items-center gap-2 text-[10px] tracking-wider transition-colors',
                isDone
                  ? 'text-[#22C55E]'
                  : isCurrent
                  ? 'text-[#38BDF8] font-bold'
                  : 'text-[#666666]'
              )}
            >
              {isDone ? (
                <span className="text-[#22C55E]">✓</span>
              ) : isCurrent ? (
                <span className="w-2 h-2 rounded-full bg-[#38BDF8] animate-ping" />
              ) : (
                <span className="text-[#666666]">○</span>
              )}
              <span>{label}</span>
            </div>
          );
        })}
      </div>

      {currentStatusText && (
        <div className="pt-1.5 text-[9px] text-[#A0A0A0] border-t border-white/10 truncate">
          STATUS: {currentStatusText}
        </div>
      )}
    </div>
  );
};
