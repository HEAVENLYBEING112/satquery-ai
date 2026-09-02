// frontend/src/pages/DashboardPage.tsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Activity,
  Scan,
  GitCompare,
  Layers,
  Terminal,
  History,
  Eye,
  PlusCircle,
  Radio,
  CheckCircle2,
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useAppStore } from '../store/useAppStore';
import { formatISODate } from '../utils/formatters';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { history, setWorkflowMode } = useAppStore();

  const handleQuickAction = (mode: 'single' | 'temporal' | 'cross_modal', path = '/workspace') => {
    setWorkflowMode(mode);
    navigate(path);
  };

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Header & Mission Control Status */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0D0D0D] border border-white/10 shadow-2xl">
        <div className="space-y-1">
          <div className="text-[10px] text-[#38BDF8] font-bold uppercase tracking-widest">
            ISRO SATELLITE COMMAND
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
            MISSION CONTROL
          </h1>
          <p className="text-xs text-[#A0A0A0]">
            SATQUERY AI INTELLIGENCE OVERVIEW
          </p>
        </div>

        {/* System Status Indicators (Green only for Online/Ready) */}
        <div className="flex flex-wrap items-center gap-3 p-2.5 rounded-xl bg-[#050505] border border-white/10 text-xs">
          <div className="flex items-center gap-2 text-white">
            <span className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse" />
            <span className="text-[11px] font-bold">SYSTEM ONLINE</span>
          </div>
          <div className="w-px h-3 bg-white/10" />
          <div className="flex items-center gap-2 text-white">
            <span className="w-2 h-2 rounded-full bg-[#22C55E]" />
            <span className="text-[11px] font-bold">ENGINE READY</span>
          </div>
          <div className="w-px h-3 bg-white/10" />
          <div className="flex items-center gap-2 text-white">
            <span className="w-2 h-2 rounded-full bg-[#22C55E]" />
            <span className="text-[11px] font-bold">AGENT CONTROLLER ACTIVE</span>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-5 space-y-2 bg-[#111111] border-white/10 relative overflow-hidden">
          <div className="absolute top-0 inset-x-0 h-0.5 bg-[#38BDF8]" />
          <div className="text-[11px] text-[#A0A0A0] uppercase tracking-wider">TOTAL ANALYSES</div>
          <div className="text-3xl font-black text-white">128</div>
          <p className="text-[10px] text-[#22C55E]">✓ System operating nominal</p>
        </Card>

        <Card className="p-5 space-y-2 bg-[#111111] border-white/10 relative overflow-hidden">
          <div className="absolute top-0 inset-x-0 h-0.5 bg-[#38BDF8]" />
          <div className="text-[11px] text-[#A0A0A0] uppercase tracking-wider">SINGLE IMAGE</div>
          <div className="text-3xl font-black text-white">64</div>
          <p className="text-[10px] text-[#A0A0A0]">RS-VQA & Grounding</p>
        </Card>

        <Card className="p-5 space-y-2 bg-[#111111] border-white/10 relative overflow-hidden">
          <div className="absolute top-0 inset-x-0 h-0.5 bg-[#38BDF8]" />
          <div className="text-[11px] text-[#A0A0A0] uppercase tracking-wider">CHANGE ANALYSIS</div>
          <div className="text-3xl font-black text-white">38</div>
          <p className="text-[10px] text-[#A0A0A0]">Bi-Temporal CDVQA</p>
        </Card>

        <Card className="p-5 space-y-2 bg-[#111111] border-white/10 relative overflow-hidden">
          <div className="absolute top-0 inset-x-0 h-0.5 bg-[#38BDF8]" />
          <div className="text-[11px] text-[#A0A0A0] uppercase tracking-wider">OPTICAL + SAR</div>
          <div className="text-3xl font-black text-white">26</div>
          <p className="text-[10px] text-[#A0A0A0]">Cross-Sensor Fusion</p>
        </Card>
      </div>

      {/* Quick Action Launchpad */}
      <div className="space-y-3">
        <div className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
          <Radio className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span>QUICK ACTIONS</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <Button
            variant="primary"
            size="md"
            onClick={() => handleQuickAction('single', '/workspace')}
            icon={<PlusCircle className="w-4 h-4" />}
            className="w-full"
          >
            NEW ANALYSIS
          </Button>

          <Button
            variant="secondary"
            size="md"
            onClick={() => handleQuickAction('temporal', '/change-detection')}
            icon={<GitCompare className="w-4 h-4 text-[#38BDF8]" />}
            className="w-full"
          >
            CHANGE DETECTION
          </Button>

          <Button
            variant="secondary"
            size="md"
            onClick={() => handleQuickAction('cross_modal', '/optical-sar')}
            icon={<Layers className="w-4 h-4 text-[#38BDF8]" />}
            className="w-full"
          >
            OPTICAL + SAR
          </Button>

          <Button
            variant="secondary"
            size="md"
            onClick={() => navigate('/history')}
            icon={<History className="w-4 h-4 text-[#38BDF8]" />}
            className="w-full"
          >
            VIEW HISTORY
          </Button>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-white uppercase tracking-widest">
            RECENT OPERATIONS
          </span>
          <Link to="/history" className="text-[11px] text-[#38BDF8] hover:underline">
            FULL MISSION LOG →
          </Link>
        </div>

        <div className="rounded-xl border border-white/10 bg-[#090909] overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#050505] text-[#A0A0A0] uppercase border-b border-white/10 text-[10px]">
              <tr>
                <th className="p-3.5">ID</th>
                <th className="p-3.5">DATE</th>
                <th className="p-3.5">TASK</th>
                <th className="p-3.5">INPUT TYPE</th>
                <th className="p-3.5">CONFIDENCE</th>
                <th className="p-3.5">STATUS</th>
                <th className="p-3.5 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-[#A0A0A0]">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-[#666666]">
                    NO PRIOR TELEMETRY LOGGED. INITIATE ANALYSIS FROM WORKSPACE.
                  </td>
                </tr>
              ) : (
                history.slice(0, 5).map((rec) => (
                  <tr key={rec.id} className="hover:bg-white/5 transition-colors">
                    <td className="p-3.5 text-white font-bold">{rec.jobId.slice(0, 8)}</td>
                    <td className="p-3.5">{formatISODate(rec.date)}</td>
                    <td className="p-3.5 uppercase text-slate-200">{rec.taskType}</td>
                    <td className="p-3.5 uppercase">{rec.inputMode}</td>
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
    </div>
  );
};
