// frontend/src/pages/ReportsPage.tsx
import React, { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { FileText, Download, Eye, FileDown, ShieldCheck, Terminal } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { ReportDossierModal } from '../components/report/ReportDossierModal';
import { downloadJsonReport } from '../services/reportService';
import { MOCK_VQA_RESULT, MOCK_TEMPORAL_RESULT, MOCK_CROSSMODAL_RESULT } from '../api/mock/mockData';

export const ReportsPage: React.FC = () => {
  const { currentResult } = useAppStore();
  const [selectedReportResult, setSelectedReportResult] = useState<any | null>(null);

  const sampleReports = [
    {
      id: 'SATQUERY_ANALYSIS_001',
      title: 'VISAKHAPATNAM PORT MARITIME DOSSIER',
      task: 'SINGLE IMAGE GROUNDING',
      date: '2026.09.02',
      status: 'COMPLETED',
      result: MOCK_VQA_RESULT,
    },
    {
      id: 'SATQUERY_ANALYSIS_002',
      title: 'BRAHMAPUTRA RIVER FLOOD INUNDATION',
      task: 'CHANGE DETECTION',
      date: '2026.09.02',
      status: 'COMPLETED',
      result: MOCK_TEMPORAL_RESULT,
    },
    {
      id: 'SATQUERY_ANALYSIS_003',
      title: 'CARTOSAT-2S & RISAT-1A CROSS-MODAL FUSION',
      task: 'OPTICAL + SAR',
      date: '2026.09.02',
      status: 'COMPLETED',
      result: MOCK_CROSSMODAL_RESULT,
    },
  ];

  return (
    <div className="space-y-6 pb-12 font-mono">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded bg-[#111111] text-[#38BDF8] text-[10px] font-bold border border-white/10 mb-2 uppercase tracking-widest">
          <FileText className="w-3 h-3" />
          <span>MISSION DOSSIERS</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight uppercase">
          INTELLIGENCE REPORTS
        </h1>
        <p className="text-xs text-[#A0A0A0] uppercase tracking-wider">
          EXPORTABLE GEOSPATIAL INTELLIGENCE & AUDIT DOSSIERS
        </p>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sampleReports.map((report) => (
          <Card key={report.id} className="p-5 space-y-4 bg-[#111111] border-white/10 hover:border-[#38BDF8]/40 transition-all flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-[10px]">
                <span className="font-bold text-[#38BDF8]">{report.id}</span>
                <span className="px-2 py-0.2 rounded font-bold uppercase bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/30">
                  ● {report.status}
                </span>
              </div>

              <div className="text-xs font-bold text-white leading-snug">
                {report.title}
              </div>

              <div className="flex items-center justify-between text-[10px] text-[#A0A0A0] pt-1">
                <span>TASK: {report.task}</span>
                <span>{report.date}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/10">
              <Button
                size="sm"
                variant="primary"
                onClick={() => setSelectedReportResult(report.result)}
                icon={<Eye className="w-3.5 h-3.5" />}
              >
                VIEW
              </Button>

              <Button
                size="sm"
                variant="secondary"
                onClick={() => downloadJsonReport(report.result, `${report.id}.json`)}
                icon={<Download className="w-3.5 h-3.5 text-[#38BDF8]" />}
              >
                DOWNLOAD
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Printable Report Modal */}
      {selectedReportResult && (
        <ReportDossierModal
          result={selectedReportResult}
          isOpen={Boolean(selectedReportResult)}
          onClose={() => setSelectedReportResult(null)}
        />
      )}
    </div>
  );
};
