// frontend/src/components/results/FallbackAlert.tsx
import React from 'react';
import { EvidenceBundle } from '../../types/engine';
import { AlertTriangle, Info } from 'lucide-react';

interface FallbackAlertProps {
  evidence?: EvidenceBundle[];
  reason?: string;
  className?: string;
}

/**
 * Checks whether fallback was triggered per SRS Section 29.1
 */
export function isFallbackTriggered(evidence: EvidenceBundle[] = []): {
  triggered: boolean;
  reason: string;
} {
  for (const bundle of evidence) {
    if (bundle.metadata?.fallback_triggered === true) {
      return {
        triggered: true,
        reason: String(bundle.metadata.fallback_reason ?? 'Hardware or dependency fallback triggered.'),
      };
    }
  }
  return { triggered: false, reason: '' };
}

export const FallbackAlert: React.FC<FallbackAlertProps> = ({ evidence = [], reason: directReason, className }) => {
  const { triggered, reason } = isFallbackTriggered(evidence);
  const activeReason = directReason || reason;

  if (!triggered && !directReason) return null;

  return (
    <div
      role="alert"
      className={`bg-amber-950/40 border-l-4 border-amber-500 p-4 rounded-r-xl border border-amber-500/20 text-amber-200 my-3 shadow-lg ${className || ''}`}
    >
      <div className="flex items-center gap-2 mb-1">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        <p className="font-semibold text-amber-300 text-xs sm:text-sm tracking-wide">
          Fallback Model Activated (OpticalSARSpecialist)
        </p>
      </div>
      <p className="text-amber-200/90 text-xs leading-relaxed">
        Advanced deep multimodal model was unavailable. Result was truthfully generated using the deterministic cross-modal analysis fallback engine.
      </p>
      {activeReason && (
        <p className="text-amber-400/90 text-[11px] font-mono mt-1.5 p-1.5 rounded bg-amber-950/80 border border-amber-500/30">
          Reason: {activeReason}
        </p>
      )}
    </div>
  );
};
