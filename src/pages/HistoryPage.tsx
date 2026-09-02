// frontend/src/pages/HistoryPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { History, Download, Trash2, Eye, Filter } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { formatISODate } from '../utils/formatters';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { history, clearHistory } = useAppStore();
  const [filterMode, setFilterMode] = useState<'all' | 'single' | 'temporal' | 'cross_modal' | 'completed' | 'failed'>('all');

  const filteredHistory = history.filter((item) => {
    if (filterMode === 'all') return true;
    if (filterMode === 'completed') return item.status === 'completed';
    if (filterMode === 'failed') return item.status === 'failed';
    return item.inputMode === filterMode;
  });

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
            <History className="w-3 h-3" />
            <span>MISSION ARCHIVE</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
            MISSION HISTORY
          </h1>
          <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
            PREVIOUS SATELLITE ANALYSIS OPERATIONS
          </p>
        </div>

        {history.length > 0 && (
          <Button size="sm" variant="secondary" onClick={clearHistory} icon={<Trash2 className="w-3.5 h-3.5 text-[#EF4444]" />}>
            PURGE ARCHIVE
          </Button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-lg bg-[#090909] border border-white/10 text-xs">
        <Filter className="w-3.5 h-3.5 text-[#38BDF8] ml-2 mr-1" />
        {[
          { id: 'all', label: 'ALL' },
          { id: 'single', label: 'SINGLE IMAGE' },
          { id: 'temporal', label: 'CHANGE' },
          { id: 'cross_modal', label: 'OPTICAL + SAR' },
          { id: 'completed', label: 'COMPLETED' },
          { id: 'failed', label: 'FAILED' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterMode(tab.id as any)}
            className={`px-3 py-1 rounded text-[10px] font-bold uppercase transition-colors cursor-pointer ${
              filterMode === tab.id
                ? 'bg-[#38BDF8] text-[#050505] font-black'
                : 'text-[#A0A0A0] hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* History Table */}
      <div className="rounded-xl border border-white/10 bg-[#090909] overflow-hidden shadow-2xl">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#050505] text-[#A0A0A0] uppercase border-b border-white/10 text-[10px]">
            <tr>
              <th className="p-3.5">ANALYSIS ID</th>
              <th className="p-3.5">TIMESTAMP</th>
              <th className="p-3.5">TASK</th>
              <th className="p-3.5">INPUT</th>
              <th className="p-3.5">QUERY</th>
              <th className="p-3.5">CONFIDENCE</th>
              <th className="p-3.5">STATUS</th>
              <th className="p-3.5 text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-[#A0A0A0]">
            {filteredHistory.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-8 text-center text-[#666666]">
                  NO HISTORICAL TELEMETRY MATCHING THE SELECTED FILTER.
                </td>
              </tr>
            ) : (
              filteredHistory.map((rec) => (
                <tr key={rec.id} className="hover:bg-white/5 transition-colors">
                  <td className="p-3.5 text-white font-bold">{rec.jobId.slice(0, 8)}</td>
                  <td className="p-3.5">{formatISODate(rec.date)}</td>
                  <td className="p-3.5 uppercase text-slate-200">{rec.taskType}</td>
                  <td className="p-3.5 uppercase">{rec.inputMode}</td>
                  <td className="p-3.5 max-w-xs truncate text-white" title={rec.query}>
                    "{rec.query}"
                  </td>
                  <td className="p-3.5 text-[#38BDF8]">
                    {rec.confidence ? `${(rec.confidence * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                  <td className="p-3.5">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        rec.status === 'completed'
                          ? 'bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/30'
                          : 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/30'
                      }`}
                    >
                      {rec.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => navigate('/workspace')}
                      className="px-2.5 py-1 rounded bg-sky-500/10 text-[#38BDF8] border border-sky-400/30 hover:bg-[#38BDF8] hover:text-black transition-colors uppercase text-[10px] font-bold cursor-pointer"
                    >
                      VIEW
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
