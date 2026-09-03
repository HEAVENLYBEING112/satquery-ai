// frontend/src/components/ui/Badge.tsx
import React from 'react';
import { clsx } from 'clsx';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'neutral' | 'success' | 'warning' | 'error' | 'sky';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className,
}) => {
  const base = 'inline-flex items-center font-mono tracking-wider uppercase rounded border transition-colors';
  const sizes = {
    sm: 'text-[10px] px-2 py-0.5 gap-1 font-semibold',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-semibold',
  };
  const variants = {
    neutral: 'bg-[#161616] text-[#A0A0A0] border-white/10',
    success: 'bg-[#22C55E]/10 text-[#22C55E] border-[#22C55E]/40',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/40',
    error: 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/40',
    sky: 'bg-[#38BDF8]/10 text-[#38BDF8] border-[#38BDF8]/40',
  };

  return (
    <span className={clsx(base, sizes[size], variants[variant], className)}>
      {children}
    </span>
  );
};
