// frontend/src/components/upload/AssetCard.tsx
import React from 'react';
import { X } from 'lucide-react';
import { UploadedFileState } from '../../types/app';
import { formatBytes } from '../../utils/formatters';
import { sanitizeText } from '../../utils/sanitize';

interface AssetCardProps {
  asset: UploadedFileState;
  onRemove: (id: string) => void;
}

export const AssetCard: React.FC<AssetCardProps> = ({ asset, onRemove }) => {
  const meta = asset.metadata;

  return (
    <div className="relative flex items-center gap-2.5 p-2.5 rounded-lg bg-[#111111] border border-white/10 hover:border-white/20 transition-all font-mono group">
      {/* Thumbnail preview */}
      <div className="w-10 h-10 rounded bg-[#050505] border border-white/10 overflow-hidden shrink-0 relative">
        <img
          src={asset.previewUrl}
          alt={sanitizeText(asset.name)}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Metadata info */}
      <div className="flex-1 min-w-0 pr-5">
        <div className="text-[11px] font-bold text-white truncate" title={asset.name}>
          {sanitizeText(asset.name)}
        </div>

        <div className="flex flex-wrap items-center gap-x-2 text-[9px] text-[#A0A0A0] mt-0.5">
          <span>{formatBytes(asset.size)}</span>
          <span>•</span>
          <span className="text-[#38BDF8]">{asset.type}</span>
          <span>•</span>
          <span className="text-[#22C55E] flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
            <span>{asset.modality.toUpperCase()} READY</span>
          </span>
        </div>
      </div>

      {/* Remove Button (Red X) */}
      <button
        onClick={() => onRemove(asset.id)}
        className="absolute top-2 right-2 p-1 rounded text-[#666666] hover:text-[#EF4444] hover:bg-white/5 transition-colors cursor-pointer"
        title="Remove Asset"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
