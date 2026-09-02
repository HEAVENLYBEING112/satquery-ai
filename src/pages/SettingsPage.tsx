// frontend/src/pages/SettingsPage.tsx
import React from 'react';
import { useAppStore } from '../store/useAppStore';
import { Settings, Sliders, Shield, Database, Save, Trash2 } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export const SettingsPage: React.FC = () => {
  const { userSettings, updateSettings, clearHistory } = useAppStore();

  return (
    <div className="space-y-6 pb-12 max-w-4xl font-mono">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
          <Settings className="w-3 h-3" />
          <span>CONFIGURATION</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
          SYSTEM SETTINGS
        </h1>
        <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
          MISSION CONTROL PREFERENCES & TELEMETRY PARAMETERS
        </p>
      </div>

      {/* 1. Interface Preferences */}
      <Card className="p-5 space-y-4 bg-[#111111] border-white/10">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Sliders className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span>INTERFACE CONFIGURATION</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1.5">
            <label className="text-[#A0A0A0] font-bold">COLOR THEME</label>
            <select
              value={userSettings.theme}
              onChange={(e) => updateSettings({ theme: e.target.value as any })}
              className="w-full bg-[#050505] border border-white/10 rounded-lg p-2.5 text-white font-mono focus:border-[#38BDF8] focus:outline-none"
            >
              <option value="dark">DEEP SPACE BLACK (DEFAULT)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[#A0A0A0] font-bold">TELEMETRY LANGUAGE</label>
            <select
              className="w-full bg-[#050505] border border-white/10 rounded-lg p-2.5 text-white font-mono focus:border-[#38BDF8] focus:outline-none"
            >
              <option>ENGLISH (ISRO SCIENTIFIC SPEC)</option>
            </select>
          </div>
        </div>
      </Card>

      {/* 2. AI & Verification Tolerances */}
      <Card className="p-5 space-y-4 bg-[#111111] border-white/10">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Shield className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span>ANALYSIS & AUDIT TOLERANCES</span>
        </h3>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-white/10">
            <div>
              <div className="font-bold text-white uppercase">AUTO-SELECT WORKFLOW</div>
              <div className="text-[10px] text-[#A0A0A0]">
                Agent dynamically detects modality and routes to specialist models
              </div>
            </div>
            <input
              type="checkbox"
              checked={userSettings.autoSelectWorkflow}
              onChange={(e) => updateSettings({ autoSelectWorkflow: e.target.checked })}
              className="w-4 h-4 rounded border-white/20 accent-[#38BDF8] cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-white/10">
            <div>
              <div className="font-bold text-white uppercase">SHOW VISUAL EVIDENCE OVERLAYS</div>
              <div className="text-[10px] text-[#A0A0A0]">
                Render spatial bounding boxes and change difference heatmaps
              </div>
            </div>
            <input
              type="checkbox"
              checked={userSettings.showEvidenceOverlays}
              onChange={(e) => updateSettings({ showEvidenceOverlays: e.target.checked })}
              className="w-4 h-4 rounded border-white/20 accent-[#38BDF8] cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-white/10">
            <div>
              <div className="font-bold text-white uppercase">SHOW AUDITABLE EXECUTION TRACES</div>
              <div className="text-[10px] text-[#A0A0A0]">
                Expose router steps, specialist fallback logs, and inference latency
              </div>
            </div>
            <input
              type="checkbox"
              checked={userSettings.showExecutionTrace}
              onChange={(e) => updateSettings({ showExecutionTrace: e.target.checked })}
              className="w-4 h-4 rounded border-white/20 accent-[#38BDF8] cursor-pointer"
            />
          </div>
        </div>
      </Card>

      {/* 3. Data & Storage */}
      <Card className="p-5 space-y-4 bg-[#111111] border-white/10">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span>DATA & TELEMETRY STORAGE</span>
        </h3>

        <div className="flex items-center justify-between text-xs">
          <div>
            <div className="font-bold text-white">MISSION HISTORY ARCHIVE</div>
            <div className="text-[10px] text-[#A0A0A0]">
              Telemetry queries and analysis logs are cached in local memory
            </div>
          </div>
          <Button
            size="sm"
            variant="danger"
            onClick={clearHistory}
            icon={<Trash2 className="w-3.5 h-3.5" />}
          >
            PURGE CACHE
          </Button>
        </div>
      </Card>
    </div>
  );
};
