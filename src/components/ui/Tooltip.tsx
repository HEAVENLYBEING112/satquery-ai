// frontend/src/components/ui/Tooltip.tsx
import React, { useState } from 'react';
import { clsx } from 'clsx';

interface TooltipProps {
  content: string | React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  className,
}) => {
  const [visible, setVisible] = useState(false);

  const posStyles = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div
      className="relative inline-flex items-center"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <div
          role="tooltip"
          className={clsx(
            'absolute z-50 px-2.5 py-1.5 text-xs text-slate-200 bg-slate-900 border border-slate-700 rounded shadow-2xl pointer-events-none whitespace-normal max-w-xs transition-opacity duration-150',
            posStyles[position],
            className
          )}
        >
          {content}
        </div>
      )}
    </div>
  );
};
