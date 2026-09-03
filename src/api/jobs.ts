// frontend/src/api/jobs.ts
import { isMockMode } from './client';
import { JobSubmitRequest, JobResponse, TraceStep, EngineResult } from '../types/engine';
import { mockSubmitJob, mockPollJob, mockGetTrace, mockGetReport } from './mock/mockService';

/**
 * Submits an analysis job to the Engine
 */
export async function submitJob(req: JobSubmitRequest): Promise<{ job_id: string }> {
  if (isMockMode()) {
    return mockSubmitJob(req);
  }
  // FUTURE BACKEND API:
  // return request<{ job_id: string }>('/api/v1/jobs', { method: 'POST', body: JSON.stringify(req) });
  return mockSubmitJob(req);
}

/**
 * Polls the current status of an ongoing analysis job
 */
export async function pollJob(jobId: string, latencyMs = 1200): Promise<JobResponse> {
  if (isMockMode()) {
    return mockPollJob(jobId, latencyMs);
  }
  // FUTURE BACKEND API:
  // return request<JobResponse>(`/api/v1/jobs/${jobId}`);
  return mockPollJob(jobId, latencyMs);
}

/**
 * Retrieves the raw execution trace for an analysis job
 */
export async function getJobTrace(jobId: string): Promise<{ job_id: string; trace: TraceStep[] }> {
  if (isMockMode()) {
    return mockGetTrace(jobId);
  }
  // FUTURE BACKEND API:
  // return request<{ job_id: string; trace: TraceStep[] }>(`/api/v1/jobs/${jobId}/trace`);
  return mockGetTrace(jobId);
}

/**
 * Downloads / fetches the generated analysis report
 */
export async function getJobReport(jobId: string): Promise<{ report_id: string; title: string; timestamp: string; engine_result: EngineResult | null }> {
  if (isMockMode()) {
    return mockGetReport(jobId);
  }
  // FUTURE BACKEND API:
  // return request<any>(`/api/v1/jobs/${jobId}/report`);
  return mockGetReport(jobId);
}
