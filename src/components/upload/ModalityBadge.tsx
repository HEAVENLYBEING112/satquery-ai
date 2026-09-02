// frontend/src/components/upload/ModalityBadge.tsx
import React from 'react';
import { Modality } from '../../types/engine';
import { MODALITY_INFO } from '../../utils/taskLabels';
import { Eye, Radio } from 'lucide-react';
import { clsx } from 'clsx';

interface ModalityBadgeProps {
  modality: Modality;
  className?: string;
}

export const ModalityBadge: React.FC<ModalityBadgeProps> = ({ modality, className }) => {
  const info = MODALITY_INFO[modality];
  const isOptical = modality === 'optical';

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium border',
        info.color,
        className
      )}
    >
      {isOptical ? <Eye className="w-3 h-3 text-sky-400" /> : <Radio className="w-3 h-3 text-amber-400" />}
      <span>{isOptical ? 'OPTICAL (VNIR)' : 'SAR (RADAR)'}</span>
    </span>
  );
};
