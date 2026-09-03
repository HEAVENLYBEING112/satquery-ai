// frontend/src/components/trace/TracePanel.tsx
import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { TraceStepItem } from './TraceStepItem';
import { ChevronUp, ChevronDown, Terminal, Activity, Layers, Cpu } from 'lucide-react';
import { clsx } from 'clsx';

export const TracePanel: React.FC = () => {
  const { isTraceOpen, toggleTraceOpen, currentResult } = useAppStore();

  const trace = currentResult?.execution_trace || [];
  const totalDuration = trace.reduce((acc, step) => acc + (step.duration_ms || 0), 0);

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 flex flex-col pointer-events-none">
      {/* Toggle button tab */}
      <div className="flex justify-end px-6 pointer-events-auto">
        <button
          onClick={toggleTraceOpen}
          className="flex items-center gap-2 px-4 py-2 rounded-t-xl bg-slate-900 border-t border-x border-slate-700 text-xs font-mono font-semibold text-slate-300 hover:text-cyan-400 hover:bg-slate-800 transition-all shadow-2xl cursor-pointer"
        >
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span>Execution Trace ({trace.length} steps)</span>
          {totalDuration > 0 && (
            <span className="text-[10px] text-slate-500 font-normal">[{totalDuration}ms]</span>
          )}
          {isTraceOpen ? <ChevronDown className="w-4 h-4 ml-1" /> : <ChevronUp className="w-4 h-4 ml-1" />}
        </button>
      </div>

      {/* Expandable Drawer */}
      {isTraceOpen && (
        <div className="bg-slate-950/95 border-t border-slate-800 backdrop-blur-xl shadow-2xl pointer-events-auto max-h-[40vh] overflow-y-auto p-4 sm:p-6 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-900 max-w-5xl mx-auto">
            <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <span className="font-bold">Auditable Execution Trace</span>
              <span className="text-slate-500">— Real-time specialist tool invocations</span>
            </div>
            <div className="text-[11px] font-mono text-cyan-400">
              Request ID: {currentResult?.request_id ? `${currentResult.request_id.slice(0, 16)}...` : 'N/A'}
            </div>
          </div>

          <div className="max-w-5xl mx-auto space-y-2">
            {trace.length === 0 ? (
              <div className="p-4 text-center rounded-xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500">
                No active execution trace. Submit a query to inspect tool sequencing and execution timelines.
              </div>
            ) : (
              trace.map((step) => <TraceStepItem key={step.step} step={step} />)
            )}
          </div>
        </div>
      )}
    </div>
  );
};
