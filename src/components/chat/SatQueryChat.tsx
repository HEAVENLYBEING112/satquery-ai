// frontend/src/components/chat/SatQueryChat.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Eye, Terminal } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { QuerySuggestions } from './QuerySuggestions';
import { ProcessingSteps } from './ProcessingSteps';
import { formatConfidence, formatISODate } from '../../utils/formatters';
import { Badge } from '../ui/Badge';

export const SatQueryChat: React.FC = () => {
  const {
    chatMessages,
    query,
    setQuery,
    runAnalysis,
    isAnalyzing,
    analysisStepText,
    files,
    setViewerLayer,
  } = useAppStore();

  const [inputVal, setInputVal] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (query) setInputVal(query);
  }, [query]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isAnalyzing]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputVal.trim() || isAnalyzing || files.length === 0) return;
    const q = inputVal.trim();
    setInputVal('');
    runAnalysis(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isSubmitDisabled = !inputVal.trim() || isAnalyzing || files.length === 0;

  return (
    <div className="flex flex-col h-full rounded-xl bg-[#090909] border border-white/10 shadow-2xl overflow-hidden font-mono">
      {/* Chat Header */}
      <div className="p-3 border-b border-white/10 bg-[#050505] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#111111] border border-sky-400/30 flex items-center justify-center text-[#38BDF8]">
            <Bot className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">SATQUERY AI</div>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[10px] text-[#38BDF8]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] animate-ping" />
          <span>READY FOR QUERY</span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-3.5 overflow-y-auto space-y-3.5">
        {chatMessages.map((msg) => {
          const isUser = msg.sender === 'user';
          const conf = msg.result ? formatConfidence(msg.result.confidence) : null;

          return (
            <div
              key={msg.id}
              className={`flex gap-2.5 text-xs leading-relaxed ${
                isUser ? 'flex-row-reverse justify-start' : 'justify-start'
              }`}
            >
              <div
                className={`w-6 h-6 rounded shrink-0 flex items-center justify-center font-bold text-[10px] ${
                  isUser
                    ? 'bg-[#38BDF8] text-[#050505]'
                    : 'bg-[#111111] border border-white/10 text-[#38BDF8]'
                }`}
              >
                {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
              </div>

              <div
                className={`p-3 rounded-lg max-w-[85%] space-y-2 ${
                  isUser
                    ? 'bg-[#1C1C1C] text-white border border-white/10'
                    : 'bg-[#050505] border-l-2 border-[#38BDF8] border-y border-r border-white/10 text-[#FFFFFF] shadow-lg'
                }`}
              >
                <div className="whitespace-pre-wrap text-[11px] leading-relaxed font-sans font-medium">
                  {msg.content}
                </div>

                {/* Evidence & Confidence meta if attached to message */}
                {msg.result && (
                  <div className="pt-2 border-t border-white/10 flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {conf && (
                        <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-sky-500/10 text-[#38BDF8] border border-sky-400/30">
                          {conf.text}
                        </span>
                      )}
                      <span className="text-[9px] text-[#666666]">
                        {formatISODate(msg.timestamp)}
                      </span>
                    </div>

                    <button
                      onClick={() => setViewerLayer('evidence')}
                      className="inline-flex items-center gap-1 text-[10px] text-[#38BDF8] hover:text-white uppercase font-bold cursor-pointer transition-colors"
                    >
                      <Eye className="w-3 h-3" />
                      <span>VIEW EVIDENCE</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Live Processing Animation */}
        {isAnalyzing && <ProcessingSteps currentStatusText={analysisStepText} />}

        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Input & Quick Commands */}
      <div className="p-3 border-t border-white/10 bg-[#050505] space-y-2.5">
        <QuerySuggestions />

        <form onSubmit={handleSubmit} className="relative">
          <textarea
            ref={textareaRef}
            rows={2}
            value={inputVal}
            maxLength={500}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              files.length === 0
                ? 'UPLOAD SATELLITE DATA TO ENABLE QUERIES...'
                : 'ENTER SATELLITE QUERY...'
            }
            disabled={files.length === 0 || isAnalyzing}
            className="w-full rounded-lg bg-[#0D0D0D] border border-white/10 p-2.5 pr-10 text-xs text-white placeholder-[#666666] focus:border-[#38BDF8] focus:outline-none resize-none font-mono disabled:opacity-40"
          />

          <div className="absolute right-2 bottom-2.5">
            <button
              type="submit"
              disabled={isSubmitDisabled}
              className="p-1.5 rounded bg-[#38BDF8] hover:bg-[#0EA5E9] disabled:bg-[#1C1C1C] disabled:text-[#666666] text-[#050505] font-bold transition-all shadow-md cursor-pointer disabled:cursor-not-allowed"
              title="Send Query"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>

        <div className="flex items-center justify-between text-[9px] text-[#666666]">
          <span>{inputVal.length}/500 CHARACTERS</span>
          <span>ENTER TO TRANSMIT</span>
        </div>
      </div>
    </div>
  );
};
