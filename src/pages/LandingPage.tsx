// frontend/src/pages/LandingPage.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import {
  Satellite,
  Scan,
  MessageSquare,
  GitCompare,
  Layers,
  Cpu,
  ShieldCheck,
  Terminal,
  Crosshair,
  Compass,
  ArrowRight,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { SAMPLE_OPTICAL_PORT } from '../api/mock/mockData';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-20 pb-20 overflow-hidden bg-[#050505]">
      {/* Hero Section */}
      <section className="relative pt-12 sm:pt-20 px-4 sm:px-6 max-w-7xl mx-auto text-center space-y-8">
        {/* Subtle Ambient Sky Glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[450px] h-[250px] bg-sky-500/10 blur-[130px] rounded-full pointer-events-none -z-10" />

        {/* ISRO Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-[#111111] border border-white/10 text-[11px] text-[#38BDF8] font-mono uppercase tracking-widest shadow-xl">
          <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] animate-pulse" />
          <span>ISRO SPACE APPLICATIONS CENTRE • SATQUERY AI</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.1] font-mono uppercase">
          ASK YOUR SATELLITE <br />
          <span className="text-[#38BDF8]">
            IMAGES ANYTHING.
          </span>
        </h1>

        <p className="text-sm sm:text-base text-[#A0A0A0] max-w-2xl mx-auto leading-relaxed">
          Transform complex remote sensing imagery into actionable intelligence through natural language and multimodal AI.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link to="/workspace">
            <Button size="lg" variant="primary" icon={<Terminal className="w-4 h-4" />}>
              LAUNCH SATQUERY AI
            </Button>
          </Link>
          <a href="#features">
            <Button size="lg" variant="secondary" icon={<ArrowRight className="w-4 h-4 text-[#38BDF8]" />}>
              EXPLORE SYSTEM
            </Button>
          </a>
        </div>

        {/* Futuristic Mission Control Preview Visual */}
        <div className="mt-12 max-w-4xl mx-auto relative rounded-2xl bg-[#090909] border border-white/10 p-4 shadow-2xl shadow-black">
          {/* Top HUD bar */}
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10 font-mono text-[10px] text-[#A0A0A0]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#22C55E]" />
              <span className="text-white font-bold">MISSION MONITOR: SYNTHETIC MOCK-SAT</span>
            </div>
            <div className="text-[#38BDF8]">COORD: 17.7021° N, 83.2245° E</div>
          </div>

          <div className="relative rounded-xl overflow-hidden bg-[#050505] border border-white/10 h-72 sm:h-96 flex items-center justify-center">
            <img
              src={SAMPLE_OPTICAL_PORT}
              alt="Satellite Intelligence Scan"
              className="w-full h-full object-cover opacity-80"
            />

            {/* Scientific Grid & Scanning Overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#38bdf810_1px,transparent_1px),linear-gradient(to_bottom,#38bdf810_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

            {/* Target Bounding Box Overlays */}
            <div className="absolute top-1/4 left-1/3 w-32 h-20 border border-[#38BDF8] bg-sky-500/10 rounded flex flex-col justify-between p-1.5 font-mono text-[9px] text-[#38BDF8]">
              <span className="font-bold">TARGET_BERTH_01</span>
              <span className="text-right text-[#22C55E]">CONFIDENCE: 94.2%</span>
            </div>

            <div className="absolute bottom-1/4 right-1/4 w-28 h-16 border border-[#22C55E] bg-emerald-500/10 rounded flex flex-col justify-between p-1.5 font-mono text-[9px] text-[#22C55E]">
              <span className="font-bold">CROSS_MODAL_WATER</span>
              <span className="text-right">SAR CONSENSUS</span>
            </div>

            {/* Floating Terminal Card */}
            <div className="absolute bottom-4 left-4 right-4 sm:right-auto sm:max-w-md p-3 rounded-xl bg-[#090909]/90 border border-white/20 backdrop-blur-md text-left font-mono text-xs space-y-1">
              <div className="text-[10px] text-[#38BDF8] flex items-center gap-1.5 font-bold">
                <Crosshair className="w-3 h-3" />
                <span>QUERY: "Identify port infrastructure and vessels"</span>
              </div>
              <p className="text-[#FFFFFF] text-[11px]">
                Deep-water maritime berths and 2 transport vessels identified with 97% cross-sensor agreement.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section */}
      <section id="features" className="px-4 sm:px-6 max-w-7xl mx-auto space-y-10 pt-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-mono uppercase">
            SPECIALIZED REMOTE SENSING CAPABILITIES
          </h2>
          <p className="text-xs text-[#A0A0A0] max-w-lg mx-auto">
            Architected specifically for satellite Earth observation and multimodal telemetry.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Feature 1 */}
          <Card className="p-6 space-y-3 bg-[#111111] border-white/10 hover:border-sky-400/50 transition-all">
            <div className="w-9 h-9 rounded-lg bg-[#090909] border border-white/10 text-[#38BDF8] flex items-center justify-center">
              <Satellite className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
              SINGLE IMAGE INTELLIGENCE
            </h3>
            <p className="text-xs text-[#A0A0A0] leading-relaxed">
              Analyze optical and SAR satellite imagery through visual question answering and scene description.
            </p>
          </Card>

          {/* Feature 2 */}
          <Card className="p-6 space-y-3 bg-[#111111] border-white/10 hover:border-sky-400/50 transition-all">
            <div className="w-9 h-9 rounded-lg bg-[#090909] border border-white/10 text-[#38BDF8] flex items-center justify-center">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
              NATURAL LANGUAGE QUERIES
            </h3>
            <p className="text-xs text-[#A0A0A0] leading-relaxed">
              Ask questions using simple human language without needing complex manual GIS pipelines.
            </p>
          </Card>

          {/* Feature 3 */}
          <Card className="p-6 space-y-3 bg-[#111111] border-white/10 hover:border-sky-400/50 transition-all">
            <div className="w-9 h-9 rounded-lg bg-[#090909] border border-white/10 text-[#38BDF8] flex items-center justify-center">
              <GitCompare className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
              CHANGE DETECTION
            </h3>
            <p className="text-xs text-[#A0A0A0] leading-relaxed">
              Identify changes across multiple satellite observations with bi-temporal difference mapping.
            </p>
          </Card>

          {/* Feature 4 */}
          <Card className="p-6 space-y-3 bg-[#111111] border-white/10 hover:border-sky-400/50 transition-all">
            <div className="w-9 h-9 rounded-lg bg-[#090909] border border-white/10 text-[#38BDF8] flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
              OPTICAL + SAR ANALYSIS
            </h3>
            <p className="text-xs text-[#A0A0A0] leading-relaxed">
              Combine complementary optical spectral data with cloud-penetrating synthetic aperture radar.
            </p>
          </Card>

          {/* Feature 5 */}
          <Card className="p-6 space-y-3 bg-[#111111] border-white/10 hover:border-sky-400/50 transition-all">
            <div className="w-9 h-9 rounded-lg bg-[#090909] border border-white/10 text-[#38BDF8] flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
              AGENTIC AI
            </h3>
            <p className="text-xs text-[#A0A0A0] leading-relaxed">
              Automatically selects, validates, and sequences the appropriate analysis workflow from a model registry.
            </p>
          </Card>

          {/* Feature 6 */}
          <Card className="p-6 space-y-3 bg-[#111111] border-white/10 hover:border-sky-400/50 transition-all">
            <div className="w-9 h-9 rounded-lg bg-[#090909] border border-white/10 text-[#38BDF8] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
              VISUAL EVIDENCE
            </h3>
            <p className="text-xs text-[#A0A0A0] leading-relaxed">
              View spatial bounding boxes, change difference heatmaps, and downloadable intelligence dossiers.
            </p>
          </Card>
        </div>
      </section>

      {/* 4-Step Workflow Section */}
      <section className="px-4 sm:px-6 max-w-7xl mx-auto space-y-10">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight font-mono uppercase">
            OPERATIONAL WORKFLOW
          </h2>
          <p className="text-xs text-[#A0A0A0]">From raw satellite bytes to verified intelligence</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
          <div className="p-5 rounded-xl bg-[#0D0D0D] border border-white/10 space-y-2">
            <div className="text-xl font-bold text-[#38BDF8]">01</div>
            <h4 className="text-xs font-bold text-white uppercase">Upload Satellite Data</h4>
            <p className="text-[11px] text-[#A0A0A0] leading-relaxed">
              Drop single, bi-temporal, or cross-modal GeoTIFF/TIFF files into the workstation.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[#0D0D0D] border border-white/10 space-y-2">
            <div className="text-xl font-bold text-[#38BDF8]">02</div>
            <h4 className="text-xs font-bold text-white uppercase">Ask a Question</h4>
            <p className="text-[11px] text-[#A0A0A0] leading-relaxed">
              Enter queries in natural English or select suggested context prompts.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[#0D0D0D] border border-white/10 space-y-2">
            <div className="text-xl font-bold text-[#38BDF8]">03</div>
            <h4 className="text-xs font-bold text-white uppercase">AI Selects Analysis</h4>
            <p className="text-[11px] text-[#A0A0A0] leading-relaxed">
              The agentic controller checks metadata and routes to specialist models.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[#0D0D0D] border border-white/10 space-y-2">
            <div className="text-xl font-bold text-[#22C55E]">04</div>
            <h4 className="text-xs font-bold text-white uppercase">Get Intelligence</h4>
            <p className="text-[11px] text-[#A0A0A0] leading-relaxed">
              Obtain verified results with spatial bounding overlays and exportable reports.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
