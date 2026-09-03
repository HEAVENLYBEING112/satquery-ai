// frontend/src/components/viewer/TemporalSlider.tsx
import React, { useState, useRef, useCallback } from 'react';
import { ChevronsLeftRight, Calendar } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { ChangeMaskOverlay } from './ChangeMaskOverlay';
import { BoundingBoxOverlay } from './BoundingBoxOverlay';

interface TemporalSliderProps {
  beforeUrl: string;
  afterUrl: string;
  beforeDate?: string;
  afterDate?: string;
}

export const TemporalSlider: React.FC<TemporalSliderProps> = ({
  beforeUrl,
  afterUrl,
  beforeDate = '2024-01-15 (T1)',
  afterDate = '2024-08-10 (T2)',
}) => {
  const { temporalSwipePosition, setTemporalSwipePosition, currentResult, viewerLayer } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setTemporalSwipePosition(percentage);
    },
    [setTemporalSwipePosition]
  );

  const onMouseDown = () => setIsDragging(true);
  const onMouseUp = () => setIsDragging(false);

  const onMouseMove = (e: React.MouseEvent) => {
    if (isDragging) handleMove(e.clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    if (e.touches[0]) handleMove(e.touches[0].clientX);
  };

  const changeMask = currentResult?.evidence?.[0]?.change_mask || null;
  const boundingBoxes = currentResult?.evidence?.[0]?.bounding_boxes || [];

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[420px] bg-slate-950 rounded-2xl overflow-hidden select-none border border-slate-800 shadow-2xl cursor-ew-resize"
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
      onTouchMove={onTouchMove}
      onTouchEnd={onMouseUp}
    >
      {/* Background Image: AFTER (T2) */}
      <div className="absolute inset-0">
        <img src={afterUrl} alt="After satellite observation" className="w-full h-full object-cover" />
        <div className="absolute top-4 right-4 px-3 py-1.5 rounded-lg bg-slate-900/80 backdrop-blur-md border border-rose-500/30 text-rose-300 text-xs font-mono font-semibold flex items-center gap-1.5 shadow-lg">
          <Calendar className="w-3.5 h-3.5 text-rose-400" />
          <span>AFTER: {afterDate}</span>
        </div>
      </div>

      {/* Foreground Image: BEFORE (T1) Clipped by swipe position */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${temporalSwipePosition}%` }}
      >
        <div className="absolute inset-0 w-full h-full" style={{ width: containerRef.current?.offsetWidth || '100%' }}>
          <img src={beforeUrl} alt="Before satellite observation" className="w-full h-full object-cover" />
        </div>
        <div className="absolute top-4 left-4 px-3 py-1.5 rounded-lg bg-slate-900/80 backdrop-blur-md border border-sky-500/30 text-sky-300 text-xs font-mono font-semibold flex items-center gap-1.5 shadow-lg">
          <Calendar className="w-3.5 h-3.5 text-sky-400" />
          <span>BEFORE: {beforeDate}</span>
        </div>
      </div>

      {/* Overlay layers */}
      {(viewerLayer === 'evidence' || viewerLayer === 'change_mask') && (
        <>
          <ChangeMaskOverlay changeMask={changeMask} opacity={0.7} />
          <BoundingBoxOverlay boxes={boundingBoxes} />
        </>
      )}

      {/* Drag Divider Handle */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-cyan-400 cursor-ew-resize z-20 shadow-[0_0_12px_rgba(6,182,212,0.8)]"
        style={{ left: `${temporalSwipePosition}%` }}
        onMouseDown={onMouseDown}
        onTouchStart={onMouseDown}
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-slate-900 border-2 border-cyan-400 shadow-xl flex items-center justify-center text-cyan-400 hover:scale-110 transition-transform">
          <ChevronsLeftRight className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
};
