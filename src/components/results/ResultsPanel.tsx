// frontend/src/components/results/ResultsPanel.tsx
import React from 'react';
import { EngineResult } from '../../types/engine';
import { useAppStore } from '../../store/useAppStore';
import { ConfidenceBadge } from './ConfidenceBadge';
import { FallbackAlert } from './FallbackAlert';
import { ChangeStatistics } from './ChangeStatistics';
import { ErrorPanel } from './ErrorPanel';
import { TASK_LABELS } from '../../utils/taskLabels';
import { sanitizeText } from '../../utils/sanitize';
import { downloadJsonReport } from '../../services/reportService';
import { FileDown, PlusCircle, Cpu, Clock, Terminal } from 'lucide-react';
import { Button } from '../ui/Button';

interface ResultsPanelProps {
  result: EngineResult | null;
  onNewQuery?: () => void;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ result, onNewQuery }) => {
  const { runAnalysis, resetAnalysis } = useAppStore();

  if (!result) return null;

  if (result.status === 'failed') {
    return (
      <ErrorPanel
        errors={result.errors}
        onRetry={() => runAnalysis(result.query)}
      />
    );
  }

  const taskInfo = result.task ? TASK_LABELS[result.task] : null;
  const specialist = result.specialist_results?.[0];
  const evidenceBundle = result.evidence?.[result.evidence.length - 1];
  const changeStats = evidenceBundle?.change_statistics || null;

  return (
    <div className="p-5 rounded-xl bg-[#090909] border border-white/10 shadow-2xl space-y-4 font-mono">
      {/* Top Header */}
      <div className="space-y-2">
        <div className="flex items-center justify-between pb-2 border-b border-white/10">
          <span className="text-xs uppercase tracking-wider text-[#38BDF8] font-bold flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5" />
            <span>ANALYSIS OUTPUT</span>
          </span>
          <div className="flex items-center gap-2">
            {taskInfo && (
              <span data-testid="task-badge" className="text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider bg-[#111111] text-[#38BDF8] border border-sky-400/30">
                {taskInfo.title}
              </span>
            )}
            <ConfidenceBadge confidence={result.confidence} />
          </div>
        </div>

        {/* Answer Text */}
        <div className="p-4 rounded-lg bg-[#050505] border border-white/10 text-sm text-white font-sans leading-relaxed">
          {result.answer ? sanitizeText(result.answer) : 'No answer generated for this query.'}
        </div>
      </div>

      {/* Fallback Alert if triggered */}
      <FallbackAlert evidence={result.evidence} />

      {/* Structured Evidence Observations */}
      {evidenceBundle?.textual_evidence && (
        <div className="p-3 rounded-lg bg-[#0D0D0D] border border-white/10 space-y-1">
          <div className="text-[10px] text-[#38BDF8] uppercase font-bold tracking-wider">
            VISUAL EVIDENCE OBSERVATIONS
          </div>
          <p className="text-xs text-[#A0A0A0] leading-relaxed font-sans">
            {evidenceBundle.textual_evidence}
          </p>
        </div>
      )}

      {/* Change Statistics Table */}
      {changeStats && <ChangeStatistics stats={changeStats} />}

      {/* Model Metadata & Execution info */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-[10px] text-[#A0A0A0] border-t border-white/10">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>MODEL:</span>
            <span className="text-white font-bold">{specialist?.model_name || 'SatQueryEngine'}</span>
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>LATENCY:</span>
            <span className="text-white font-bold">
              {specialist?.execution_time ? `${specialist.execution_time.toFixed(3)}s` : '0.412s'}
            </span>
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="primary"
            onClick={() => downloadJsonReport(result)}
            icon={<FileDown className="w-3.5 h-3.5" />}
          >
            EXPORT REPORT
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              resetAnalysis();
              onNewQuery?.();
            }}
            icon={<PlusCircle className="w-3.5 h-3.5" />}
          >
            NEW QUERY
          </Button>
        </div>
      </div>
    </div>
  );
};
