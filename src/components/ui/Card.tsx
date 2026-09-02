// frontend/src/components/ui/Card.tsx
import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glow' | 'panel' | 'subtle';
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  className,
  ...props
}) => {
  const base = 'rounded-xl border transition-all duration-150';
  const variants = {
    default: 'bg-[#111111] border-white/10 shadow-xl shadow-black/80 hover:border-sky-500/30',
    glow: 'bg-[#111111] border-sky-400/40 shadow-2xl shadow-sky-950/20',
    panel: 'bg-[#0D0D0D] border-white/10',
    subtle: 'bg-[#080808] border-white/5',
  };

  return (
    <div className={clsx(base, variants[variant], className)} {...props}>
      {children}
    </div>
  );
};
