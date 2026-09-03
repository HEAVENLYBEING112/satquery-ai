// frontend/src/components/ui/Spinner.tsx
import React from 'react';
import { clsx } from 'clsx';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  label?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className, label }) => {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-10 h-10 border-3',
    xl: 'w-16 h-16 border-4',
  };

  return (
    <div className={clsx('flex flex-col items-center justify-center gap-3', className)}>
      <div className="relative flex items-center justify-center">
        {/* Outer pulsing ring */}
        <div className={clsx('rounded-full border-t-indigo-500 border-r-indigo-500/30 border-b-transparent border-l-transparent animate-spin', sizes[size])} />
        {/* Inner radar dot */}
        <div className="absolute w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
      </div>
      {label && <span className="text-xs text-slate-400 font-mono tracking-wider animate-pulse">{label}</span>}
    </div>
  );
};
