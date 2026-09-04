// frontend/src/pages/OpticalSarPage.tsx
import React, { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { ImageViewer } from '../components/viewer/ImageViewer';
import { ResultsPanel } from '../components/results/ResultsPanel';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Layers, Radio, Eye, Send } from 'lucide-react';
import { SAMPLE_DATASETS } from '../api/mock/mockData';

export const OpticalSarPage: React.FC = () => {
  const { runAnalysis, isAnalyzing, currentResult, setWorkflowMode, loadPreset } = useAppStore();
  const [crossQuery, setCrossQuery] = useState('Classify using SAR and optical images together');

  const handleRun = () => {
    setWorkflowMode('cross_modal');
    runAnalysis(crossQuery);
  };

  const handleLoadCartosatRisat = () => {
    const preset = SAMPLE_DATASETS.find((d) => d.id === 'synthetic-coastal-port');
    if (preset) void loadPreset(preset);
  };

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
            <Layers className="w-3 h-3" />
            <span>CROSS-MODAL SENSOR FUSION</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
            CROSS-MODAL SATELLITE INTELLIGENCE
          </h1>
          <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
            COMBINE OPTICAL AND RADAR DATA FOR ENHANCED ANALYSIS.
          </p>
        </div>

        <Button size="sm" variant="secondary" onClick={handleLoadCartosatRisat} icon={<Radio className="w-3.5 h-3.5 text-[#38BDF8]" />}>
          LOAD SYNTHETIC OPTICAL/SAR PAIR
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Fusion Workstation (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="p-5 space-y-4 bg-[#111111] border-white/10">
            <div className="text-xs font-bold text-white uppercase tracking-wider">
              MULTIMODAL FUSION DIRECTIVE:
            </div>

            <textarea
              rows={3}
              value={crossQuery}
              onChange={(e) => setCrossQuery(e.target.value)}
              className="w-full rounded-lg bg-[#050505] border border-white/10 p-3 text-xs text-white focus:border-[#38BDF8] focus:outline-none"
              placeholder="Ask how optical and radar sensors can be jointly analyzed..."
            />

            <div className="p-3 rounded-lg bg-[#050505] border border-white/10 space-y-2 text-xs">
              <div className="font-bold text-white uppercase text-[10px] tracking-wider">
                COMPLEMENTARY MODALITY BREAKDOWN:
              </div>
              <div className="space-y-1.5 text-[#A0A0A0] text-[11px]">
                <div className="flex items-start gap-2">
                  <Eye className="w-3.5 h-3.5 text-[#38BDF8] shrink-0 mt-0.5" />
                  <span><strong>OPTICAL (VNIR):</strong> Multispectral RGB, NDVI vegetation indices, water absorption.</span>
                </div>
                <div className="flex items-start gap-2">
                  <Radio className="w-3.5 h-3.5 text-[#38BDF8] shrink-0 mt-0.5" />
                  <span><strong>SAR (C-BAND):</strong> Cloud penetration, day/night radar backscatter, metallic dihedral reflection.</span>
                </div>
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              className="w-full"
              isLoading={isAnalyzing}
              onClick={handleRun}
              icon={<Send className="w-3.5 h-3.5" />}
            >
              EXECUTE OPTICAL + SAR FUSION
            </Button>
          </Card>
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
