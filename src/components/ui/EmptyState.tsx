// frontend/src/components/ui/EmptyState.tsx
import React from 'react';
import { Satellite, ImagePlus } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = <Satellite className="w-12 h-12 text-slate-600" />,
  title,
  description,
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-950/40 min-h-[280px]">
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-indigo-400 mb-4 shadow-inner">
        {icon}
      </div>
      <h4 className="text-base font-medium text-slate-200 mb-1">{title}</h4>
      <p className="text-xs text-slate-400 max-w-sm mb-5 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button size="sm" variant="secondary" onClick={onAction} icon={<ImagePlus className="w-4 h-4" />}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
