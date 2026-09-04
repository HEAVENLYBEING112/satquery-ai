// frontend/src/types/app.ts
import { EngineResult, JobResponse, Modality, Role, TaskType } from './engine';

export type AppWorkflowMode = 'single' | 'temporal' | 'cross_modal';

export interface UploadedFileState {
  file: File;
  id: string;
  name: string;
  size: number;
  type: string;
  previewUrl: string;
  modality: Modality;
  role?: Role;
  acquisitionDate?: string;
  progress: number;
  uploaded: boolean;
  error?: string;
  metadata?: {
    bands?: number;
    crs?: string;
    resolution?: number;
    width?: number;
    height?: number;
    sensor?: string;
    satellite?: string;
  };
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  isLoading?: boolean;
  result?: EngineResult;
  error?: string;
  suggestedAction?: string;
}

export interface SampleDataset {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  mode: AppWorkflowMode;
  badge: string;
  recommendedQueries: string[];
  images: Array<{
    name: string;
    previewUrl: string;
    fileUrl?: string;
    modality: Modality;
    role?: Role;
    acquisitionDate?: string;
    metadata: {
      bands: number;
      crs: string;
      resolution: number;
      width: number;
      height: number;
      sensor: string;
      satellite: string;
    };
  }>;
}

export interface HistoryRecord {
  id: string;
  jobId: string;
  date: string;
  taskType: TaskType;
  inputMode: AppWorkflowMode;
  query: string;
  confidence: number | null;
  status: 'completed' | 'failed' | 'running';
  answerSummary: string;
  imagePreviews: string[];
  engineResult: EngineResult;
}

export interface SystemHealthState {
  aiServices: 'online' | 'degraded' | 'offline';
  analysisEngine: 'ready' | 'busy' | 'offline';
  satellitePipeline: 'ready' | 'calibrating' | 'offline';
  engineMode: 'mock' | 'real';
  version: string;
  lastPing: string;
}

export interface UserSettings {
  theme: 'dark' | 'light';
  language: string;
  defaultMode: AppWorkflowMode;
  autoSelectWorkflow: boolean;
  confidenceThreshold: number;
  showTraceByDefault: boolean;
  showVisualEvidence: boolean;
  showEvidenceOverlays: boolean;
  showExecutionTrace: boolean;
  mockSimulatedLatencyMs: number;
  showMockBanner: boolean;
}
