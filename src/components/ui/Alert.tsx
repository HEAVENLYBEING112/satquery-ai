// frontend/src/components/ui/Alert.tsx
import React from 'react';
import { clsx } from 'clsx';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

export interface AlertProps {
  variant?: 'warning' | 'error' | 'success' | 'info';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'warning',
  title,
  children,
  className,
}) => {
  const icons = {
    warning: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    info: <Info className="w-5 h-5 text-sky-400 shrink-0" />,
  };

  const styles = {
    warning: 'bg-amber-950/40 border-l-4 border-amber-500 text-amber-200',
    error: 'bg-rose-950/40 border-l-4 border-rose-500 text-rose-200',
    success: 'bg-emerald-950/40 border-l-4 border-emerald-500 text-emerald-200',
    info: 'bg-sky-950/40 border-l-4 border-sky-500 text-sky-200',
  };

  return (
    <div
      role="alert"
      className={clsx('p-3.5 rounded-r-lg border border-slate-800 flex items-start gap-3 text-xs md:text-sm', styles[variant], className)}
    >
      {icons[variant]}
      <div className="flex-1">
        {title && <h5 className="font-semibold mb-1 tracking-wide">{title}</h5>}
        <div className="opacity-90 leading-relaxed">{children}</div>
      </div>
    </div>
  );
};
