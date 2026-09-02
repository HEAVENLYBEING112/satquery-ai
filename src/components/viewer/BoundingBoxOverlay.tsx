// frontend/src/components/viewer/BoundingBoxOverlay.tsx
import React from 'react';
import { BoundingBox } from '../../types/engine';
import { useAppStore } from '../../store/useAppStore';

interface BoundingBoxOverlayProps {
  boxes: BoundingBox[];
  imageWidth?: number;
  imageHeight?: number;
}

export const BoundingBoxOverlay: React.FC<BoundingBoxOverlayProps> = ({
  boxes,
  imageWidth = 600,
  imageHeight = 600,
}) => {
  const { selectedBoundingBox, setSelectedBoundingBox } = useAppStore();

  if (!boxes || boxes.length === 0) return null;

  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-auto"
      viewBox={`0 0 ${imageWidth} ${imageHeight}`}
      preserveAspectRatio="none"
    >
      <defs>
        {/* Glow filter for highlighted boxes */}
        <filter id="box-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#38bdf8" />
        </filter>
      </defs>

      {boxes.map((box, index) => {
        const [xmin, ymin, xmax, ymax] = box.coordinates;
        const width = Math.max(10, xmax - xmin);
        const height = Math.max(10, ymax - ymin);

        // Color coding based on SRS Section 18.1 & 26.2
        const labelLower = box.label.toLowerCase();
        const sourceLower = box.source.toLowerCase();

        let strokeColor = '#6366f1'; // default indigo
        let fillColor = 'rgba(99, 102, 241, 0.15)';
        let strokeDash = 'none';

        if (sourceLower === 'cross_modal' || labelLower.includes('agreement')) {
          strokeColor = '#10b981'; // solid green for cross-modal agreement
          fillColor = 'rgba(16, 185, 129, 0.2)';
        } else if (sourceLower === 'sar') {
          strokeColor = '#f97316'; // orange dashed for SAR
          strokeDash = '6,4';
          fillColor = 'rgba(249, 115, 22, 0.15)';
        } else if (sourceLower === 'optical') {
          strokeColor = '#3b82f6'; // blue dashed for Optical
          strokeDash = '6,4';
          fillColor = 'rgba(59, 130, 246, 0.15)';
        } else if (labelLower.includes('water')) {
          strokeColor = '#38bdf8'; // sky blue
          fillColor = 'rgba(56, 189, 248, 0.2)';
        } else if (labelLower.includes('built') || labelLower.includes('vessel') || labelLower.includes('pier')) {
          strokeColor = '#f59e0b'; // amber
          fillColor = 'rgba(245, 158, 11, 0.2)';
        } else if (labelLower.includes('change') || labelLower.includes('inundat')) {
          strokeColor = '#ef4444'; // red
          fillColor = 'rgba(239, 68, 68, 0.25)';
        }

        const isSelected = selectedBoundingBox === box;

        return (
          <g
            key={`bbox-${index}`}
            className="cursor-pointer transition-all duration-150 group"
            onClick={() => setSelectedBoundingBox(isSelected ? null : box)}
          >
            {/* Hit area */}
            <rect
              x={xmin}
              y={ymin}
              width={width}
              height={height}
              fill={fillColor}
              stroke={strokeColor}
              strokeWidth={isSelected ? 3 : 2}
              strokeDasharray={strokeDash}
              filter={isSelected ? 'url(#box-glow)' : undefined}
              className="hover:stroke-cyan-300 transition-colors"
            />

            {/* Corner brackets */}
            <line x1={xmin} y1={ymin} x2={xmin + 8} y2={ymin} stroke="#fff" strokeWidth={2} />
            <line x1={xmin} y1={ymin} x2={xmin} y2={ymin + 8} stroke="#fff" strokeWidth={2} />
            <line x1={xmax} y1={ymax} x2={xmax - 8} y2={ymax} stroke="#fff" strokeWidth={2} />
            <line x1={xmax} y1={ymax} x2={xmax} y2={ymax - 8} stroke="#fff" strokeWidth={2} />

            {/* Tag Badge */}
            <rect
              x={xmin}
              y={Math.max(0, ymin - 22)}
              width={Math.min(180, box.label.length * 8 + 40)}
              height={20}
              fill="#090d16"
              rx={3}
              stroke={strokeColor}
              strokeWidth={1}
            />
            <text
              x={xmin + 6}
              y={Math.max(14, ymin - 8)}
              fill="#f8fafc"
              fontSize="10"
              fontFamily="monospace"
              fontWeight="bold"
            >
              {box.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
