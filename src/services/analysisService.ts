// frontend/src/services/analysisService.ts
// ============================================================================
// SATQUERY AI - SATELLITE INTELLIGENCE SERVICE LAYER
// ============================================================================
// FUTURE: Replace mock response with backend API call.
// When backend endpoints are deployed, update VITE_USE_MOCK=false and set
// VITE_API_BASE_URL to point to the real ISRO SAC engine FastAPI server.
// ============================================================================

import { uploadAsset } from '../api/assets';
import { submitJob, pollJob, getJobTrace } from '../api/jobs';
import { EngineResult, JobResponse, Modality, Role } from '../types/engine';
import { UploadedFileState } from '../types/app';

export interface RunAnalysisParams {
  query: string;
  files: UploadedFileState[];
  onProgress?: (status: string, elapsedMs: number) => void;
  latencyMs?: number;
}

/**
 * High-level analysis workflow:
 * 1. Upload files if not already uploaded (POST /api/v1/assets/upload)
 * 2. Submit analysis job (POST /api/v1/jobs/submit)
 * 3. Poll until completed or failed (GET /api/v1/jobs/:id/status)
 * 4. Return unified EngineResult
 */
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

  onProgress?.('Validating input assets and georeferencing metadata...', 100);

  // 1. Prepare assets payload
  const assetsPayload = files.map((f, idx) => ({
    asset_id: f.id || `asset-mock-${idx}`,
    modality: f.modality || ('optical' as Modality),
    role: f.role || (idx === 0 ? ('before' as Role) : ('after' as Role)),
    acquisition_time: f.acquisitionDate,
  }));

  onProgress?.('Submitting job to SatQuery Agentic Controller...', 300);

  // 2. Submit job (FUTURE: calls real backend POST /api/v1/jobs/submit)
  const { job_id } = await submitJob({
    query,
    assets: assetsPayload,
  });

  onProgress?.('Agent is selecting specialist model from registry...', 600);

  // 3. Poll job lifecycle (FUTURE: calls real backend GET /api/v1/jobs/:id/status)
  const startTime = Date.now();
  const pollIntervalMs = 250;
  const timeoutMs = 30000;

  while (Date.now() - startTime < timeoutMs) {
    const elapsed = Date.now() - startTime;
    if (elapsed > 400) {
      onProgress?.('Executing remote sensing vision-language pipeline...', elapsed);
    }
    if (elapsed > 900) {
      onProgress?.('Synthesizing evidence overlays and confidence bounds...', elapsed);
    }

    const jobResponse: JobResponse = await pollJob(job_id, latencyMs);

    if (jobResponse.status === 'completed' && jobResponse.result) {
      return jobResponse.result;
    }

    if (jobResponse.status === 'failed') {
      if (jobResponse.result) {
        return jobResponse.result;
      }
      throw new Error('Engine analysis failed without returning structured result.');
    }

    await new Promise((r) => setTimeout(r, pollIntervalMs));
  }

  throw new Error('Analysis request timed out after 30 seconds.');
}
