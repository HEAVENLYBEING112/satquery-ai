// frontend/src/components/viewer/ChangeMaskOverlay.tsx
import React from 'react';
import { ChangeMask } from '../../types/engine';

interface ChangeMaskOverlayProps {
  changeMask: ChangeMask | null;
  opacity?: number;
}

export const ChangeMaskOverlay: React.FC<ChangeMaskOverlayProps> = ({
  changeMask,
  opacity = 0.65,
}) => {
  if (!changeMask || !changeMask.mask_url) return null;

  return (
    <div
      className="absolute inset-0 pointer-events-none transition-opacity duration-200"
      style={{ opacity }}
    >
      <img
        src={changeMask.mask_url}
        alt="Temporal Change Detection Mask"
        className="w-full h-full object-cover mix-blend-screen"
      />
    </div>
  );
};
