// frontend/src/components/trace/TraceStepItem.tsx
import React from 'react';
import { TraceStep } from '../../types/engine';
import { CheckCircle2, AlertCircle, ChevronDown, Clock, Wrench } from 'lucide-react';

interface TraceStepItemProps {
  step: TraceStep;
}

export const TraceStepItem: React.FC<TraceStepItemProps> = ({ step }) => {
  const isSuccess = step.status === 'success';

  return (
    <details className="group rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs font-mono overflow-hidden transition-colors hover:border-slate-700">
      <summary className="flex items-center justify-between p-3 cursor-pointer select-none">
        <div className="flex items-center gap-3">
          <span className="w-5 h-5 rounded-full bg-slate-900 border border-slate-700 text-slate-300 flex items-center justify-center text-[10px] font-bold">
            {step.step}
          </span>
          <div className="flex items-center gap-2">
            <Wrench className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-bold text-slate-200">{step.tool}</span>
          </div>
          <span className="text-slate-500 hidden sm:inline">({step.task})</span>
        </div>

        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1 text-slate-400 text-[11px]">
            <Clock className="w-3 h-3 text-indigo-400" />
            <span>{step.duration_ms}ms</span>
          </span>
          {isSuccess ? (
            <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px]">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">success</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-rose-400 text-[11px]">
              <AlertCircle className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">error</span>
            </span>
          )}
          <ChevronDown className="w-4 h-4 text-slate-500 group-open:rotate-180 transition-transform" />
        </div>
      </summary>

      <div className="p-3.5 pt-0 border-t border-slate-900 bg-slate-950/40 space-y-2 text-[11px]">
        {step.result_summary !== undefined && (
          <div>
            <div className="text-slate-500 mb-1">Result Summary:</div>
            <div className="p-2 rounded bg-slate-900 text-slate-300">
              {typeof step.result_summary === 'object'
                ? JSON.stringify(step.result_summary, null, 2)
                : String(step.result_summary)}
            </div>
          </div>
        )}

        <div>
          <div className="text-slate-500 mb-1">Permitted Parameters:</div>
          <pre className="p-2 rounded bg-slate-900 text-slate-400 overflow-x-auto text-[10px]">
            {JSON.stringify(step.parameters, null, 2)}
          </pre>
        </div>
      </div>
    </details>
  );
};
