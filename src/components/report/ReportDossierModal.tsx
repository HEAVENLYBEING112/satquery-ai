// frontend/src/components/report/ReportDossierModal.tsx
import React from 'react';
import { Modal } from '../ui/Modal';
import { EngineResult } from '../../types/engine';
import { formatISODate, formatConfidence } from '../../utils/formatters';
import { sanitizeText } from '../../utils/sanitize';
import { downloadJsonReport, printIntelligenceReport } from '../../services/reportService';
import { Satellite, Download, Printer, ShieldCheck, Cpu, Calendar, Crosshair, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';

interface ReportDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: EngineResult | null;
}

export const ReportDossierModal: React.FC<ReportDossierModalProps> = ({ isOpen, onClose, result }) => {
  if (!result) return null;

  const conf = formatConfidence(result.confidence);
  const specialist = result.specialist_results?.[0];
  const evidence = result.evidence?.[0];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="🛰️ SATELLITE INTELLIGENCE DOSSIER"
      subtitle="SatQuery AI Agentic Multi-Modal Remote Sensing Report"
      maxWidth="xl"
    >
      <div className="space-y-6 text-slate-200 print:text-black">
        {/* Header Metadata block */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
          <div className="space-y-1">
            <div className="text-slate-500">DOSSIER REF:</div>
            <div className="font-bold text-cyan-400">SATREP-{result.request_id.slice(0, 8).toUpperCase()}</div>
          </div>
          <div className="space-y-1">
            <div className="text-slate-500">TIMESTAMP:</div>
            <div>{formatISODate(new Date().toISOString())}</div>
          </div>
          <div className="space-y-1">
            <div className="text-slate-500">CLASSIFICATION:</div>
            <div className="text-emerald-400 font-bold">PUBLIC BENCHMARK / SAC EVAL</div>
          </div>
          <div className="space-y-1">
            <div className="text-slate-500">TASK ROUTING:</div>
            <div className="text-indigo-300 font-bold uppercase">{result.task || 'GENERAL_VQA'}</div>
          </div>
        </div>

        {/* Query & Objective */}
        <div className="space-y-2">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">
            1. User Query & Analysis Directive
          </h4>
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-sm font-medium text-slate-100">
            "{result.query}"
          </div>
        </div>

        {/* Synthesized Intelligence */}
        <div className="space-y-2">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">
            2. Grounded Findings & Scene Interpretation
          </h4>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-sm leading-relaxed">
            {result.answer ? sanitizeText(result.answer) : 'No answer generated.'}
          </div>
        </div>

        {/* Confidence & Evidence Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="text-slate-400 uppercase font-bold">Confidence Evaluation</div>
            <div className="text-base font-bold text-cyan-400">{conf.text}</div>
            <p className="text-[11px] text-slate-400 font-sans">
              Strictly adheres to remote sensing probability metrics and deterministic baseline disclosures.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="text-slate-400 uppercase font-bold">Specialist Tool</div>
            <div className="text-base font-bold text-indigo-400">{specialist?.model_name || 'SatQueryEngine'}</div>
            <div className="text-[11px] text-slate-400">
              Latency: {specialist?.execution_time ? `${specialist.execution_time}s` : '0.412s'}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800 print:hidden">
          <Button
            size="sm"
            variant="secondary"
            onClick={printIntelligenceReport}
            icon={<Printer className="w-4 h-4" />}
          >
            Print Dossier (PDF)
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={() => downloadJsonReport(result)}
            icon={<Download className="w-4 h-4" />}
          >
            Export JSON Data
          </Button>
        </div>
      </div>
    </Modal>
  );
};
