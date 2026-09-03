// frontend/src/pages/ChangeDetectionPage.tsx
import React, { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { ImageViewer } from '../components/viewer/ImageViewer';
import { ResultsPanel } from '../components/results/ResultsPanel';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { GitCompare, Calendar, Send } from 'lucide-react';
import { SAMPLE_DATASETS } from '../api/mock/mockData';

export const ChangeDetectionPage: React.FC = () => {
  const { runAnalysis, isAnalyzing, currentResult, setWorkflowMode, loadPreset } = useAppStore();
  const [temporalQuery, setTemporalQuery] = useState('What changed between these two dates and where did the change occur?');

  const quickTemporalQueries = [
    'What changed between these two dates?',
    'Where did the inundation change occur?',
    'Did built-up area increase or decrease?',
    'Quantify the vegetation change percentage.',
  ];

  const handleRun = (q?: string) => {
    setWorkflowMode('temporal');
    runAnalysis(q || temporalQuery);
  };

  const handleLoadBrahmaputra = () => {
    const preset = SAMPLE_DATASETS.find((d) => d.id === 'brahmaputra-flood-temporal');
    if (preset) loadPreset(preset);
  };

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
            <GitCompare className="w-3 h-3" />
            <span>BI-TEMPORAL EARTH OBSERVATION</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
            MULTITEMPORAL CHANGE ANALYSIS
          </h1>
          <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
            COMPARE SATELLITE OBSERVATIONS ACROSS TIME.
          </p>
        </div>

        <Button size="sm" variant="secondary" onClick={handleLoadBrahmaputra} icon={<Calendar className="w-3.5 h-3.5 text-[#38BDF8]" />}>
          LOAD T1/T2 FLOOD MONITORING PAIR
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Temporal Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="p-5 space-y-4 bg-[#111111] border-white/10">
            <div className="text-xs font-bold text-white uppercase tracking-wider">
              CHANGE-VQA DIRECTIVE:
            </div>

            <textarea
              rows={3}
              value={temporalQuery}
              onChange={(e) => setTemporalQuery(e.target.value)}
              className="w-full rounded-lg bg-[#050505] border border-white/10 p-3 text-xs text-white focus:border-[#38BDF8] focus:outline-none"
              placeholder="Ask about differences between T1 and T2 observations..."
            />

            {/* Quick Questions */}
            <div className="space-y-1.5">
              <span className="text-[10px] text-[#A0A0A0] uppercase font-bold">
                SUGGESTED CHANGE QUERIES:
              </span>
              <div className="flex flex-col gap-1.5">
                {quickTemporalQueries.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setTemporalQuery(q);
                      handleRun(q);
                    }}
                    className="p-2 rounded bg-[#050505] border border-white/10 text-xs text-left text-[#A0A0A0] hover:text-white hover:border-[#38BDF8] transition-colors cursor-pointer"
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              className="w-full"
              isLoading={isAnalyzing}
              onClick={() => handleRun()}
              icon={<Send className="w-3.5 h-3.5" />}
            >
              EXECUTE CHANGE DETECTION
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
