// frontend/src/services/analysisService.ts
// ============================================================================
// SATQUERY AI - SATELLITE INTELLIGENCE SERVICE LAYER
// ============================================================================
// FUTURE: Replace mock response with backend API call.
// When backend endpoints are deployed, update VITE_USE_MOCK=false and set
// VITE_API_BASE_URL to point to the real ISRO SAC engine FastAPI server.
// ============================================================================

import { EngineResult, Modality, Role } from '../types/engine';
import { UploadedFileState } from '../types/app';
import { getApiBaseUrl, isMockMode } from '../api/client';
import { submitJob, pollJob } from '../api/jobs';

export interface RunAnalysisParams {
  query: string;
  files: UploadedFileState[];
  onProgress?: (status: string, elapsedMs: number) => void;
  latencyMs?: number;
}

export async function executeRemoteSensingAnalysis({
  query,
  files,
  onProgress,
  latencyMs = 1200,
}: RunAnalysisParams): Promise<EngineResult> {
  if (files.length === 0) {
    throw new Error('At least one satellite image is required.');
  }
  if (!query || query.trim().length === 0) {
    throw new Error('Please enter a natural language question or select a prompt.');
  }

  // Preserve existing mock fallback if explicitly configured
  if (isMockMode()) {
    onProgress?.('Submitting mock job...', 300);
    const assetsPayload = files.map((f, idx) => ({
      asset_id: f.id || `asset-mock-${idx}`,
      modality: f.modality || ('optical' as Modality),
      role: f.role || (idx === 0 ? ('before' as Role) : ('after' as Role)),
      acquisition_time: f.acquisitionDate,
    }));
    const { job_id } = await submitJob({ query, assets: assetsPayload });
    const startTime = Date.now();
    while (Date.now() - startTime < 30000) {
      const jobResponse = await pollJob(job_id, latencyMs);
      if (jobResponse.status === 'completed' && jobResponse.result) return jobResponse.result;
      if (jobResponse.status === 'failed') {
        if (jobResponse.result) return jobResponse.result;
        throw new Error('Engine analysis failed.');
      }
      await new Promise((r) => setTimeout(r, 250));
    }
    throw new Error('Timeout');
  }

  onProgress?.('Preparing synchronous analysis request...', 100);

  const formData = new FormData();
  formData.append('query', query);
  
  files.forEach(f => {
    if (f.file) {
      formData.append('files', f.file, f.file.name);
    }
  });

  onProgress?.('Uploading files and waiting for engine execution...', 500);

  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errMsg = `Backend error ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        if (Array.isArray(errJson.detail)) errMsg = errJson.detail.map((e: any) => e.msg).join(', ');
        else errMsg = errJson.detail;
      }
    } catch (e) {}
    throw new Error(errMsg);
  }

  onProgress?.('Rendering results...', 1000);
  const result: EngineResult = await response.json();
  return result;
}
