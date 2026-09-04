// frontend/src/components/upload/RoleAssignment.tsx
import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { Modality, Role } from '../../types/engine';
import { Layers, AlertCircle, CheckCircle2 } from 'lucide-react';

export const RoleAssignment: React.FC = () => {
  const { files, workflowMode, updateFileRole, updateFileModality } = useAppStore();

  if (files.length !== 2) return null;

  const isTemporal = workflowMode === 'temporal';
  const file1 = files[0];
  const file2 = files[1];

  const hasRoleConflict = isTemporal
    ? file1.role === file2.role
    : file1.modality === file2.modality;

  return (
    <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <h5 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>{isTemporal ? 'Bi-Temporal Role Assignment' : 'Cross-Modal Sensor Assignment'}</span>
        </h5>
        {hasRoleConflict ? (
          <span className="text-[10px] text-amber-400 flex items-center gap-1 font-mono">
            <AlertCircle className="w-3 h-3" />
            Roles must be distinct
          </span>
        ) : (
          <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-mono">
            <CheckCircle2 className="w-3 h-3" />
            Configured
          </span>
        )}
      </div>

      <div className="space-y-2.5">
        {/* File 1 Assignment */}
        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
          <div className="text-[11px] text-slate-300 font-mono truncate" title={file1.name}>
            1. {file1.name}
          </div>
          {isTemporal ? (
            <div className="flex items-center gap-2">
              <label className="text-[10px] text-slate-400 uppercase">Role:</label>
              <select
                value={file1.role || 'before'}
                onChange={(e) => updateFileRole(file1.id, e.target.value as Role)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono focus:border-cyan-400 focus:outline-none"
              >
                <option value="before">BEFORE (T1)</option>
                <option value="after">AFTER (T2)</option>
              </select>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <label className="text-[10px] text-slate-400 uppercase">Sensor:</label>
              <select
                value={file1.modality || 'optical'}
                onChange={(e) => updateFileModality(file1.id, e.target.value as Modality)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono focus:border-cyan-400 focus:outline-none"
              >
                <option value="optical">Optical (RGB/NIR)</option>
                <option value="sar">SAR (C-Band Radar)</option>
              </select>
            </div>
          )}
        </div>

        {/* File 2 Assignment */}
        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
          <div className="text-[11px] text-slate-300 font-mono truncate" title={file2.name}>
            2. {file2.name}
          </div>
          {isTemporal ? (
            <div className="flex items-center gap-2">
              <label className="text-[10px] text-slate-400 uppercase">Role:</label>
              <select
                value={file2.role || 'after'}
                onChange={(e) => updateFileRole(file2.id, e.target.value as Role)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono focus:border-cyan-400 focus:outline-none"
              >
                <option value="before">BEFORE (T1)</option>
                <option value="after">AFTER (T2)</option>
              </select>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <label className="text-[10px] text-slate-400 uppercase">Sensor:</label>
              <select
                value={file2.modality || 'sar'}
                onChange={(e) => updateFileModality(file2.id, e.target.value as Modality)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono focus:border-cyan-400 focus:outline-none"
              >
                <option value="optical">Optical (RGB/NIR)</option>
                <option value="sar">SAR (C-Band Radar)</option>
              </select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
