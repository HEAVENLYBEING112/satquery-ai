// frontend/src/pages/SingleImagePage.tsx
import React, { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { ImageViewer } from '../components/viewer/ImageViewer';
import { ResultsPanel } from '../components/results/ResultsPanel';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Scan, MessageSquare, FileText, Crosshair, Sparkles, Send } from 'lucide-react';
import { SamplePresets } from '../components/upload/SamplePresets';

export const SingleImagePage: React.FC = () => {
  const { runAnalysis, isAnalyzing, currentResult, setWorkflowMode } = useAppStore();
  const [activeTask, setActiveTask] = useState<'vqa' | 'caption' | 'grounding'>('vqa');
  const [vqaQuery, setVqaQuery] = useState('What land cover is visible in this satellite scene?');
  const [groundQuery, setGroundQuery] = useState('Highlight the cargo vessels and docking piers');

  const handleExecute = (task: 'vqa' | 'caption' | 'grounding') => {
    setWorkflowMode('single');
    if (task === 'vqa') {
      runAnalysis(vqaQuery);
    } else if (task === 'caption') {
      runAnalysis('Describe this remote sensing scene and its key objects in full detail.');
    } else if (task === 'grounding') {
      runAnalysis(groundQuery);
    }
  };

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Page Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
          <Scan className="w-3 h-3" />
          <span>SINGLE-IMAGE TELEMETRY</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
          SINGLE IMAGE INTELLIGENCE
        </h1>
        <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
          ANALYZE SATELLITE OBSERVATIONS USING AI.
        </p>
      </div>

      {/* 3 Numbered Scientific Modes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <button
          onClick={() => setActiveTask('vqa')}
          className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
            activeTask === 'vqa'
              ? 'bg-[#161616] border-[#38BDF8] shadow-lg shadow-sky-500/10'
              : 'bg-[#111111] border-white/10 hover:border-white/20'
          }`}
        >
          <div className="text-lg font-black text-[#38BDF8] mb-1">01</div>
          <div className="text-xs font-bold text-white uppercase">VISUAL QUESTION ANSWERING</div>
          <p className="text-[10px] text-[#A0A0A0] mt-1">Ask questions about the satellite image.</p>
        </button>

        <button
          onClick={() => setActiveTask('caption')}
          className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
            activeTask === 'caption'
              ? 'bg-[#161616] border-[#38BDF8] shadow-lg shadow-sky-500/10'
              : 'bg-[#111111] border-white/10 hover:border-white/20'
          }`}
        >
          <div className="text-lg font-black text-[#38BDF8] mb-1">02</div>
          <div className="text-xs font-bold text-white uppercase">SCENE DESCRIPTION</div>
          <p className="text-[10px] text-[#A0A0A0] mt-1">Generate an automated AI description.</p>
        </button>

        <button
          onClick={() => setActiveTask('grounding')}
          className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
            activeTask === 'grounding'
              ? 'bg-[#161616] border-[#38BDF8] shadow-lg shadow-sky-500/10'
              : 'bg-[#111111] border-white/10 hover:border-white/20'
          }`}
        >
          <div className="text-lg font-black text-[#38BDF8] mb-1">03</div>
          <div className="text-xs font-bold text-white uppercase">REGION GROUNDING</div>
          <p className="text-[10px] text-[#A0A0A0] mt-1">Locate targets using text queries.</p>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Task Input (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="p-5 space-y-4 bg-[#111111] border-white/10">
            {activeTask === 'vqa' && (
              <div className="space-y-3">
                <label className="text-xs font-bold text-white uppercase tracking-wider">
                  QUESTION DIRECTIVE:
                </label>
                <textarea
                  rows={3}
                  value={vqaQuery}
                  onChange={(e) => setVqaQuery(e.target.value)}
                  className="w-full rounded-lg bg-[#050505] border border-white/10 p-3 text-xs text-white focus:border-[#38BDF8] focus:outline-none"
                  placeholder="e.g. What is the dominant land cover?"
                />
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  isLoading={isAnalyzing}
                  onClick={() => handleExecute('vqa')}
                  icon={<Send className="w-3.5 h-3.5" />}
                >
                  TRANSMIT VQA QUERY
                </Button>
              </div>
            )}

            {activeTask === 'caption' && (
              <div className="space-y-3">
                <p className="text-xs text-[#A0A0A0] leading-relaxed">
                  Synthesize an exhaustive technical description analyzing optical reflectance, land cover classification, and structural characteristics.
                </p>
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  isLoading={isAnalyzing}
                  onClick={() => handleExecute('caption')}
                  icon={<Sparkles className="w-3.5 h-3.5" />}
                >
                  GENERATE SCENE DESCRIPTION
                </Button>
              </div>
            )}

            {activeTask === 'grounding' && (
              <div className="space-y-3">
                <label className="text-xs font-bold text-white uppercase tracking-wider">
                  GROUNDING QUERY:
                </label>
                <input
                  type="text"
                  value={groundQuery}
                  onChange={(e) => setGroundQuery(e.target.value)}
                  className="w-full rounded-lg bg-[#050505] border border-white/10 p-3 text-xs text-white focus:border-[#38BDF8] focus:outline-none"
                  placeholder="e.g. Highlight cargo vessels and docking piers"
                />
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  isLoading={isAnalyzing}
                  onClick={() => handleExecute('grounding')}
                  icon={<Crosshair className="w-3.5 h-3.5" />}
                >
                  EXTRACT BOUNDING COORDINATES
                </Button>
              </div>
            )}
          </Card>

          <SamplePresets />
        </div>

        {/* Right Column: Viewport & Results (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="h-[440px]">
            <ImageViewer />
          </div>

          {currentResult && <ResultsPanel result={currentResult} />}
        </div>
      </div>
    </div>
  );
};
