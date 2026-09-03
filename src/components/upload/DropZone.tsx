// frontend/src/components/upload/DropZone.tsx
import React, { useRef } from 'react';
import { UploadCloud, AlertCircle, AlertTriangle } from 'lucide-react';
import { useFileUpload } from '../../hooks/useFileUpload';
import { useAppStore } from '../../store/useAppStore';
import { AssetCard } from './AssetCard';
import { RoleAssignment } from './RoleAssignment';
import { SamplePresets } from './SamplePresets';
import { clsx } from 'clsx';

export const DropZone: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { files, removeFile } = useAppStore();
  const {
    isDragging,
    errorMessage,
    warningMessage,
    onDragOver,
    onDragLeave,
    onDrop,
    validateAndAddFiles,
  } = useFileUpload();

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(e.target.files);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="space-y-3 font-mono">
      {/* Upload Drop Container */}
      <div
        tabIndex={0}
        role="button"
        aria-label="Upload remote sensing satellite imagery"
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onKeyDown={handleKeyDown}
        onClick={() => fileInputRef.current?.click()}
        className={clsx(
          'p-4 rounded-xl border-2 border-dashed transition-all duration-150 cursor-pointer text-center flex flex-col items-center justify-center gap-2 focus:outline-none focus:ring-1 focus:ring-sky-400',
          isDragging
            ? 'border-[#38BDF8] bg-sky-950/20'
            : 'border-white/15 bg-[#0D0D0D] hover:border-white/30 hover:bg-[#111111]'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".tif,.tiff,.png,.jpg,.jpeg"
          multiple
          className="hidden"
          onChange={handleFileInputChange}
        />

        <div className="w-8 h-8 rounded-lg bg-[#050505] border border-white/10 flex items-center justify-center text-[#38BDF8]">
          <UploadCloud className="w-4 h-4" />
        </div>

        <div>
          <div className="text-xs font-bold text-white uppercase tracking-wider">
            DROP SATELLITE DATA HERE
          </div>
          <p className="text-[10px] text-[#A0A0A0] mt-0.5">
            GeoTIFF, TIFF, PNG, JPEG (MAX 2 FILES, 50MB)
          </p>
        </div>
      </div>

      {/* Warning & Error notifications (Red for errors) */}
      {warningMessage && (
        <div className="flex items-center gap-2 p-2 rounded bg-amber-950/30 border border-amber-500/40 text-amber-300 text-[10px]">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>{warningMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2 p-2 rounded bg-[#EF4444]/10 border border-[#EF4444]/40 text-[#EF4444] text-[10px]">
          <AlertCircle className="w-3.5 h-3.5 text-[#EF4444] shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Active Uploaded Assets List */}
      {files.length > 0 && (
        <div className="space-y-1.5">
          <div className="text-[10px] uppercase tracking-wider text-[#A0A0A0] font-bold">
            LOADED TELEMETRY ({files.length}/2)
          </div>
          <div className="space-y-1.5">
            {files.map((file) => (
              <AssetCard key={file.id} asset={file} onRemove={removeFile} />
            ))}
          </div>
        </div>
      )}

      {/* Role Assignment if 2 files present */}
      <RoleAssignment />

      {/* Benchmark Presets */}
      <SamplePresets />
    </div>
  );
};
