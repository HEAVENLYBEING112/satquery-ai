// frontend/src/types/engine.ts
// Verbatim definitions verified against Python dataclasses in engine/contracts.py

export type TaskType =
  | 'single_image_vqa'
  | 'single_image_caption'
  | 'single_image_grounding'
  | 'temporal_change_detection'
  | 'temporal_change_description'
  | 'temporal_change_vqa'
  | 'cross_modal_optical_sar'
  | 'croma_classification';

export type InputType =
  | 'single_optical'
  | 'single_multispectral'
  | 'single_sar'
  | 'temporal_optical'
  | 'temporal_sar'
  | 'optical_sar_pair';

export type JobStatus =
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type Modality = 'optical' | 'sar';
export type Role = 'before' | 'after';
export type CoordinateType = 'pixel' | 'geo';

export interface BoundingBox {
  label: string; // e.g. 'water_agreement', 'changed_region', 'built_area'
  coordinates: [number, number, number, number]; // [xmin, ymin, xmax, ymax]
  coordinate_type: CoordinateType; // added by backend normalization
  confidence: number | null; // NULLABLE - preserved as null
  source: string; // 'optical' | 'sar' | 'cross_modal' | 'croma_classifier' | 'model'
}

export interface ChangeMask {
  width: number;
  height: number;
  mask_url: string | null; // backend converts mask_path to URL
  threshold_used: number | null;
  changed_pixel_count: number;
  changed_fraction: number;
}

export interface EvidenceBundle {
  textual_evidence: string | null;
  bounding_boxes: BoundingBox[];
  visualizations: string[]; // list of fully-qualified URLs
  change_statistics: Record<string, unknown> | null;
  change_mask: ChangeMask | null;
  metadata: Record<string, unknown>; // may contain fallback_triggered, fallback_reason
}

export interface EngineError {
  code: string; // 'PLANNING_FAILED' | 'INVALID_WORKFLOW' | 'MODEL_EXECUTION_FAILED' | etc.
  message: string;
}

export interface TraceStep {
  step: number;
  tool: string;
  task: string;
  status: string;
  parameters: Record<string, unknown>;
  duration_ms: number;
  result_summary: unknown;
}

export interface SpecialistResult {
  status: string;
  model_name: string;
  task: TaskType;
  answer: string | null;
  confidence: number | null; // nullable — NEVER replace with 0 or 1
  evidence: EvidenceBundle;
  metadata: Record<string, unknown>;
  execution_time: number; // seconds
  error: string | null;
}

export interface EngineResult {
  request_id: string;
  status: 'success' | 'failed';
  query: string;
  task: TaskType | null;
  answer: string | null;
  confidence: number | null; // nullable — NEVER replace with any default
  specialist_results: SpecialistResult[];
  evidence: EvidenceBundle[];
  execution_trace: TraceStep[];
  errors: EngineError[];
}

// API-level contracts
export interface AssetUploadResponse {
  asset_id: string;
  filename: string;
  size_bytes: number;
  format: string;
  width: number | null;
  height: number | null;
  bands: number | null;
  crs: string | null;
  resolution: number | null;
  bbox: [number, number, number, number] | null;
  preview_url?: string;
}

export interface JobSubmitRequest {
  query: string;
  assets: Array<{
    asset_id: string;
    modality: Modality;
    role?: Role;
    acquisition_time?: string;
  }>;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  result: EngineResult | null;
}

export interface ApiError {
  code: string;
  message: string;
  details: unknown;
}

export interface CapabilitiesResponse {
  tasks: TaskType[];
  input_types: InputType[];
  supported_formats: string[];
  max_upload_bytes: number;
  models: {
    mock: string[];
    real: string[];
  };
}

export interface HealthResponse {
  status: string;
  version: string;
  engine_mode: string;
  timestamp: string;
}
