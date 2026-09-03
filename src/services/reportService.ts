// frontend/src/services/reportService.ts
import { EngineResult } from '../types/engine';
import { formatISODate } from '../utils/formatters';

export interface ExportReportData {
  reportId: string;
  generatedAt: string;
  system: string;
  result: EngineResult;
}

/**
 * Generates and triggers download of JSON intelligence report
 */
export function downloadJsonReport(result: EngineResult, filename = 'SatQuery_Intelligence_Report.json') {
  const data: ExportReportData = {
    reportId: `SATREP-${result.request_id.substring(0, 8).toUpperCase()}`,
    generatedAt: new Date().toISOString(),
    system: 'SatQuery AI Multi-Modal Remote Sensing Intelligence Platform',
    result,
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Triggers browser print dialog for printable PDF report
 */
export function printIntelligenceReport() {
  window.print();
}
