// frontend/src/components/results/ConfidenceBadge.tsx
import React from 'react';
import { formatConfidence } from '../../utils/formatters';
import { Tooltip } from '../ui/Tooltip';
import { ShieldCheck } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: number | null | undefined;
  className?: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence, className }) => {
  const { text, percentage, isAvailable } = formatConfidence(confidence);

  return (
    <Tooltip
      content="Confidence reflects the verified probability estimate from the specialized classifier. When the deterministic baseline runs, no statistical confidence is produced."
    >
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#111111] border border-white/10 font-mono text-[10px] font-bold uppercase tracking-wider cursor-help ${className || ''}`}>
        <ShieldCheck className="w-3.5 h-3.5 text-[#38BDF8]" />
        <span className="text-[#A0A0A0]">CONFIDENCE:</span>
        <span className={isAvailable ? 'text-[#38BDF8]' : 'text-[#666666]'}>
          {isAvailable ? `${percentage}` : 'N/A'}
        </span>
      </div>
    </Tooltip>
  );
};
