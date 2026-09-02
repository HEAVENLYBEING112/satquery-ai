// frontend/src/pages/WorkspacePage.tsx
import React from 'react';
import { useAppStore } from '../store/useAppStore';
import { DropZone } from '../components/upload/DropZone';
import { ImageViewer } from '../components/viewer/ImageViewer';
import { SatQueryChat } from '../components/chat/SatQueryChat';
import { ResultsPanel } from '../components/results/ResultsPanel';
import { Tabs } from '../components/ui/Tabs';
import { Scan, GitCompare, Layers, Compass, Radio } from 'lucide-react';
import { AppWorkflowMode } from '../types/app';

export const WorkspacePage: React.FC = () => {
  const { workflowMode, setWorkflowMode, currentResult } = useAppStore();

  const workflowTabs = [
    { id: 'single', label: 'SINGLE IMAGE', icon: <Scan className="w-3.5 h-3.5" /> },
    { id: 'temporal', label: 'CHANGE ANALYSIS', icon: <GitCompare className="w-3.5 h-3.5" /> },
    { id: 'cross_modal', label: 'OPTICAL + SAR', icon: <Layers className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="space-y-4 pb-12 font-mono">
      {/* Top Workflow Mode Switcher Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-[#090909] border border-white/10 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-white">
            <Radio className="w-4 h-4 text-[#38BDF8]" />
            <span>MODALITY:</span>
          </div>
          <Tabs
            tabs={workflowTabs}
            activeTab={workflowMode}
            onChange={(id) => setWorkflowMode(id as AppWorkflowMode)}
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-[#A0A0A0]">
          <span className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse" />
          <span className="text-white font-bold">MISSION ENGINE ACTIVE</span>
        </div>
      </div>

      {/* Main 3-Section Grid Workstation */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-210px)] min-h-[640px]">
        {/* Left: Input Configuration Panel (3 cols) */}
        <div className="lg:col-span-3 rounded-xl bg-[#090909] border border-white/10 p-3.5 overflow-y-auto shadow-xl space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 border-b border-white/10">
            <span className="text-xs font-bold uppercase tracking-wider text-[#38BDF8]">
              INPUT CONFIGURATION
            </span>
          </div>
          <DropZone />
        </div>

        {/* Center: Satellite Viewport Panel (5 cols) */}
        <div className="lg:col-span-5 h-full flex flex-col">
          <ImageViewer />
        </div>

        {/* Right: SatQuery AI Assistant (4 cols) */}
        <div className="lg:col-span-4 h-full flex flex-col">
          <SatQueryChat />
        </div>
      </div>

      {/* Structured Result Summary Panel */}
      {currentResult && (
        <div className="mt-4">
          <ResultsPanel result={currentResult} />
        </div>
      )}
    </div>
  );
};
