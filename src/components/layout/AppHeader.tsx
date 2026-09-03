// frontend/src/components/layout/AppHeader.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Satellite, HelpCircle, Terminal } from 'lucide-react';
import { Modal } from '../ui/Modal';

export const AppHeader: React.FC = () => {
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  return (
    <>
      <header className="h-16 border-b border-white/10 bg-[#090909]/95 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-4 sm:px-6">
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-[#111111] border border-sky-400/40 p-1 flex items-center justify-center shadow-lg shadow-sky-500/10 group-hover:border-sky-400 transition-colors">
              <Satellite className="w-5 h-5 text-[#38BDF8]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-black tracking-widest text-white font-mono">SATQUERY AI</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-sky-500/10 text-[#38BDF8] font-mono font-bold border border-sky-400/30">
                  ISRO SAC
                </span>
              </div>
              <p className="text-[10px] text-[#A0A0A0] font-mono hidden md:block uppercase tracking-wider">
                Mission Control • Remote Sensing Intelligence
              </p>
            </div>
          </Link>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsHelpOpen(true)}
            className="p-2 text-[#A0A0A0] hover:text-white hover:bg-white/5 rounded-lg border border-transparent hover:border-white/10 transition-colors cursor-pointer"
            title="System Documentation & Prompts"
          >
            <HelpCircle className="w-4 h-4 text-[#38BDF8]" />
          </button>

          <Link
            to="/workspace"
            className="inline-flex items-center gap-2 text-xs font-mono font-bold tracking-wider uppercase px-4 py-2 rounded-lg bg-[#38BDF8] hover:bg-[#0EA5E9] text-[#050505] shadow-lg shadow-sky-500/20 border border-sky-300 transition-all cursor-pointer"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Launch Platform</span>
          </Link>
        </div>
      </header>

      {/* Help Modal */}
      <Modal
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        title="🛰️ SATQUERY AI — MISSION CONTROL SPECIFICATION"
        subtitle="ISRO Space Applications Centre • Multimodal Remote Sensing Architecture"
      >
        <div className="space-y-4 text-xs text-[#A0A0A0] font-mono leading-relaxed">
          <div className="p-4 rounded-xl bg-[#050505] border border-white/10 space-y-2">
            <h5 className="font-bold text-[#38BDF8] uppercase tracking-wider text-xs">
              Operational Modalities
            </h5>
            <ul className="list-disc pl-4 space-y-1.5 text-slate-300">
              <li>
                <strong className="text-white">Single-Image VQA & Grounding:</strong> Natural language interrogation over optical/SAR raster inputs.
              </li>
              <li>
                <strong className="text-white">Bi-Temporal Change Analysis:</strong> Co-registered $T_1$ and $T_2$ observation difference mapping.
              </li>
              <li>
                <strong className="text-white">Optical + SAR Cross-Modal Fusion:</strong> Joint feature extraction combining optical reflectance with radar backscatter.
              </li>
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-[#050505] border border-white/10 space-y-1">
            <h5 className="font-bold text-[#22C55E] uppercase tracking-wider text-xs">
              Scientific Precision & Verifiability
            </h5>
            <p className="text-slate-400">
              Confidence is strictly reported as <code className="text-white">Confidence: N/A</code> when deterministic non-probabilistic models run. Fallbacks to baseline specialists are immediately made auditable.
            </p>
          </div>
        </div>
      </Modal>
    </>
  );
};
