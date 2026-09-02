// frontend/src/api/mock/mockService.ts
import {
  AssetUploadResponse,
  CapabilitiesResponse,
  EngineResult,
  HealthResponse,
  JobResponse,
  JobSubmitRequest,
  Modality,
} from '../../types/engine';
import {
  MOCK_CAPABILITIES,
  MOCK_CROSSMODAL_RESULT,
  MOCK_FAILED_RESULT,
  MOCK_GROUNDING_RESULT,
  MOCK_HEALTH,
  MOCK_TEMPORAL_RESULT,
  MOCK_VQA_RESULT,
  SAMPLE_OPTICAL_PORT,
} from './mockData';

// Helper sleep function
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Active jobs in-memory cache
const jobsStore = new Map<string, { job: JobResponse; createdAt: number; targetResult: EngineResult }>();

/**
 * Intelligent mock routing logic matching Section 8.12 of SRS
 */
function routeMockResult(query: string, assets: JobSubmitRequest['assets']): EngineResult {
  const q = query.toLowerCase();
  const count = assets.length;
  const modalities = assets.map((a) => a.modality);
  const isCrossModal = count === 2 && (modalities.includes('optical') && modalities.includes('sar'));

  // 1. Cross-modal Optical + SAR queries
  if (isCrossModal || q.includes('sar') || q.includes('radar') || q.includes('fuse') || q.includes('cross')) {
    const copy = JSON.parse(JSON.stringify(MOCK_CROSSMODAL_RESULT));
    copy.query = query;
    return copy;
  }

  // 2. Bi-temporal change queries
  if (count === 2 || q.includes('change') || q.includes('difference') || q.includes('before') || q.includes('after') || q.includes('flood')) {
    if (count === 1) {
      // Simulate failure if only 1 image provided for temporal query
      const errCopy = JSON.parse(JSON.stringify(MOCK_FAILED_RESULT));
      errCopy.query = query;
      return errCopy;
    }
    const copy = JSON.parse(JSON.stringify(MOCK_TEMPORAL_RESULT));
    copy.query = query;
    return copy;
  }

  // 3. Grounding / localization queries
  if (q.includes('highlight') || q.includes('ground') || q.includes('locate') || q.includes('where') || q.includes('detect') || q.includes('box')) {
    const copy = JSON.parse(JSON.stringify(MOCK_GROUNDING_RESULT));
    copy.query = query;
    return copy;
  }

  // 4. Default single image VQA / captioning
  const copy = JSON.parse(JSON.stringify(MOCK_VQA_RESULT));
  copy.query = query;
  if (q.includes('water') || q.includes('river') || q.includes('ocean')) {
    copy.answer = 'Water-covered regions and maritime channels were identified primarily in the eastern section of the scene.';
  } else if (q.includes('building') || q.includes('structure') || q.includes('urban')) {
    copy.answer = 'Several built-up structures, industrial storage facilities, and transport corridors were detected, concentrated in the northern quadrant.';
  }
  return copy;
}

export async function mockUploadAsset(file: File, modality: Modality = 'optical'): Promise<AssetUploadResponse> {
  await sleep(400); // simulate upload latency

  // File size check: warn if >40MB, error if >50MB
  if (file.size > 52428800) {
    throw new Error('File exceeds maximum allowed size of 50MB.');
  }

  const assetId = 'asset-' + Math.random().toString(36).substring(2, 9);
  const previewUrl = URL.createObjectURL(file);

  return {
    asset_id: assetId,
    filename: file.name,
    size_bytes: file.size,
    format: file.name.toLowerCase().endsWith('.tif') || file.name.toLowerCase().endsWith('.tiff') ? 'GeoTIFF' : 'RasterImage',
    width: 600,
    height: 600,
    bands: modality === 'optical' ? 4 : 2,
    crs: 'EPSG:32643',
    resolution: modality === 'optical' ? 0.6 : 1.25,
    bbox: [77.1, 12.9, 77.5, 13.2],
    preview_url: previewUrl,
  };
}

export async function mockSubmitJob(req: JobSubmitRequest): Promise<{ job_id: string }> {
  await sleep(350);

  if (!req.query || req.query.trim().length === 0) {
    throw new Error('Query string is required.');
  }
  if (!req.assets || req.assets.length === 0) {
    throw new Error('At least one satellite image asset is required.');
  }

  const jobId = 'job-' + Math.random().toString(36).substring(2, 10);
  const targetResult = routeMockResult(req.query, req.assets);

  const initialJob: JobResponse = {
    job_id: jobId,
    status: 'running',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    result: null,
  };

  jobsStore.set(jobId, {
    job: initialJob,
    createdAt: Date.now(),
    targetResult,
  });

  return { job_id: jobId };
}

export async function mockPollJob(jobId: string, latencyMs = 1200): Promise<JobResponse> {
  await sleep(250);

  const entry = jobsStore.get(jobId);
  if (!entry) {
    throw new Error(`Job ${jobId} not found.`);
  }

  const elapsed = Date.now() - entry.createdAt;
  if (elapsed >= latencyMs) {
    // Complete the job
    const completedJob: JobResponse = {
      ...entry.job,
      status: entry.targetResult.status === 'failed' ? 'failed' : 'completed',
      updated_at: new Date().toISOString(),
      result: entry.targetResult,
    };
    jobsStore.set(jobId, { ...entry, job: completedJob });
    return completedJob;
  }

  // Still running
  return {
    ...entry.job,
    status: 'running',
    updated_at: new Date().toISOString(),
  };
}

export async function mockGetTrace(jobId: string) {
  await sleep(150);
  const entry = jobsStore.get(jobId);
  if (!entry || !entry.job.result) {
    return { job_id: jobId, trace: [] };
  }
  return {
    job_id: jobId,
    trace: entry.job.result.execution_trace,
  };
}

export async function mockGetReport(jobId: string) {
  await sleep(200);
  const entry = jobsStore.get(jobId);
  return {
    report_id: `rep-${jobId}`,
    title: 'SatQuery AI Satellite Intelligence Analysis Report',
    timestamp: new Date().toISOString(),
    engine_result: entry ? entry.job.result : MOCK_VQA_RESULT,
  };
}

export async function mockGetCapabilities(): Promise<CapabilitiesResponse> {
  await sleep(100);
  return MOCK_CAPABILITIES;
}

export async function mockGetHealth(): Promise<HealthResponse> {
  await sleep(100);
  return {
    ...MOCK_HEALTH,
    timestamp: new Date().toISOString(),
  };
}
