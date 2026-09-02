// frontend/src/components/chat/QuerySuggestions.tsx
import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { Terminal } from 'lucide-react';

export const QuerySuggestions: React.FC = () => {
  const { files, setQuery, runAnalysis, isAnalyzing } = useAppStore();

  if (files.length === 0) return null;

  const quickCommands = [
    'DESCRIBE IMAGE',
    'IDENTIFY WATER',
    'DETECT BUILDINGS',
    'ANALYZE VEGETATION',
    'WHAT CHANGED?',
    'COMPARE LAND COVER',
  ];

  const handleSelect = (text: string) => {
    setQuery(text);
    runAnalysis(text);
  };

  return (
    <div className="space-y-1.5 font-mono">
      <div className="flex items-center gap-1.5 text-[9px] text-[#A0A0A0] uppercase tracking-widest font-bold">
        <Terminal className="w-3 h-3 text-[#38BDF8]" />
        <span>QUICK COMMANDS</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {quickCommands.map((text, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isAnalyzing}
            onClick={() => handleSelect(text)}
            className="px-2 py-0.5 text-[10px] uppercase font-bold rounded bg-[#0D0D0D] border border-white/10 text-[#A0A0A0] hover:text-white hover:border-[#38BDF8] hover:bg-white/5 transition-all text-left cursor-pointer disabled:opacity-40"
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
};
