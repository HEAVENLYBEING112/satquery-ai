// frontend/src/components/ui/Button.tsx
import React from 'react';
import { clsx } from 'clsx';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  className,
  icon,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-mono tracking-wider uppercase text-xs transition-all duration-150 rounded-lg focus:outline-none focus:ring-1 focus:ring-sky-400 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer select-none';

  const sizeStyles = {
    sm: 'px-3 py-1.5 gap-1.5 text-[11px] font-medium',
    md: 'px-4 py-2 gap-2 font-semibold',
    lg: 'px-6 py-3 gap-2.5 text-sm font-bold',
  };

  const variantStyles = {
    primary: 'bg-[#38BDF8] hover:bg-[#0EA5E9] text-[#050505] shadow-lg shadow-sky-500/15 border border-sky-300 font-bold active:scale-[0.99]',
    secondary: 'bg-[#0D0D0D] hover:bg-[#161616] text-white border border-white/20 hover:border-white/40 active:scale-[0.99]',
    outline: 'bg-transparent hover:bg-white/5 text-slate-300 border border-white/10 hover:border-sky-400 hover:text-sky-300',
    ghost: 'bg-transparent hover:bg-white/5 text-slate-400 hover:text-white',
    danger: 'bg-[#EF4444] hover:bg-red-600 text-white border border-red-400 font-bold shadow-lg shadow-red-500/20',
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={clsx(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      {...props}
    >
      {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin text-current" /> : icon}
      {children}
    </button>
  );
};
