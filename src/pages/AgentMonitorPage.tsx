// frontend/src/pages/AgentMonitorPage.tsx
import React from 'react';
import { useAppStore } from '../store/useAppStore';
import { Card } from '../components/ui/Card';
import { TraceStep } from '../types/engine';
import {
  Cpu,
  Workflow,
  CheckCircle2,
  Database,
  Terminal,
  Clock,
} from 'lucide-react';
import { MOCK_VQA_RESULT } from '../api/mock/mockData';

export const AgentMonitorPage: React.FC = () => {
  const { currentResult } = useAppStore();
  const activeResult = currentResult || MOCK_VQA_RESULT;
  const trace: TraceStep[] = activeResult.execution_trace || [];

  const pipelineStages = [
    { title: 'USER QUERY', desc: 'Query ingest and telemetry tokenization' },
    { title: 'QUERY INTERPRETATION', desc: 'Intent extraction and linguistic normalization' },
    { title: 'TASK CLASSIFICATION', desc: 'Route to RS-VQA, Grounding, or ChangeFormer' },
    { title: 'INPUT VALIDATION', desc: 'Raster bounds, CRS alignment, and sensor compatibility' },
    { title: 'MODEL SELECTION', desc: 'Load domain weights from SAC Model Registry' },
    { title: 'SPECIALIST EXECUTION', desc: 'Inference across optical/SAR tensor backbones' },
    { title: 'RESULT INTEGRATION', desc: 'Evidence bundle synthesis and confidence evaluation' },
    { title: 'FINAL RESPONSE', desc: 'Payload delivery to Mission Control HUD' },
  ];

  const modelRegistry = [
    { name: 'REMOTE SENSING VQA', version: 'v2.4-SAC', modality: 'Optical (RGB/NIR)', status: 'READY' },
    { name: 'SCENE CAPTIONING', version: 'v1.8-SAC', modality: 'Optical / SAR', status: 'READY' },
    { name: 'TEXT GROUNDING', version: 'v3.1-SAC', modality: 'Optical High-Res', status: 'READY' },
    { name: 'CHANGE DETECTION', version: 'v2.0-CD', modality: 'Bi-Temporal Pairs', status: 'READY' },
    { name: 'OPTICAL-SAR FUSION', version: 'v1.5-CROMA', modality: 'Cross-Modal Sensors', status: 'READY' },
  ];

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Page Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
          <Cpu className="w-3 h-3" />
          <span>AUTONOMOUS AGENT ORCHESTRATION</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
          AGENTIC ORCHESTRATION
        </h1>
        <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
          REAL-TIME WORKFLOW EXECUTION MONITOR
        </p>
      </div>

      {/* Execution Pipeline Overview */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
            <Workflow className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>EXECUTION PIPELINE STAGES</span>
          </span>
          <span className="text-[10px] text-[#22C55E] flex items-center gap-1 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
            <span>PIPELINE HEALTHY</span>
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {pipelineStages.map((stage, idx) => (
            <Card key={idx} className="p-3.5 space-y-1.5 bg-[#111111] border-white/10 relative">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-[#38BDF8] font-bold">0{idx + 1}</span>
                <span className="text-[#22C55E] flex items-center gap-1 font-bold">
                  <span className="w-1 h-1 rounded-full bg-[#22C55E]" />
                  <span>ONLINE</span>
                </span>
              </div>
              <div className="text-xs font-bold text-white">{stage.title}</div>
              <p className="text-[10px] text-[#A0A0A0] leading-tight">{stage.desc}</p>
            </Card>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Model Registry (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>MODEL REGISTRY</span>
          </div>

          <div className="space-y-2">
            {modelRegistry.map((mod, idx) => (
              <Card key={idx} className="p-3.5 bg-[#111111] border-white/10 space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-3.5 h-3.5 text-[#38BDF8]" />
                    <span className="text-xs font-bold text-white">{mod.name}</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.2 rounded font-bold uppercase bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/30">
                    ● {mod.status}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[10px] text-[#A0A0A0]">
                  <span>WEIGHTS: {mod.version}</span>
                  <span className="text-slate-300">{mod.modality}</span>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Live Execution Trace (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-white uppercase tracking-widest">
            <span className="flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-[#38BDF8]" />
              <span>ACTIVE TRACE LOG ({trace.length} STEPS)</span>
            </span>
          </div>

          <Card className="p-4 bg-[#090909] border-white/10 space-y-3">
            <div className="space-y-2">
              {trace.map((step: TraceStep, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-[#050505] border border-white/10 space-y-1 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-[#38BDF8] font-bold">
                        STEP {step.step}:
                      </span>
                      <span className="font-bold text-white uppercase">{step.tool}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] text-[#A0A0A0] flex items-center gap-1">
                        <Clock className="w-3 h-3 text-[#38BDF8]" />
                        <span>{step.duration_ms}ms</span>
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded font-bold uppercase bg-[#22C55E]/10 text-[#22C55E]">
                        {step.status}
                      </span>
                    </div>
                  </div>
                  <div className="text-[11px] text-[#A0A0A0] font-sans">
                    Task: <code className="text-[#38BDF8]">{step.task}</code> — {typeof step.result_summary === 'string' ? step.result_summary : JSON.stringify(step.result_summary)}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
