// frontend/src/store/useAppStore.ts
import { create } from 'zustand';
import { EngineResult, BoundingBox, Modality, Role, TaskType } from '../types/engine';
import { AppWorkflowMode, ChatMessage, HistoryRecord, SampleDataset, UploadedFileState, UserSettings } from '../types/app';
import { SAMPLE_DATASETS, MOCK_VQA_RESULT, SAMPLE_OPTICAL_PORT, SAMPLE_SAR_PORT } from '../api/mock/mockData';
import { executeRemoteSensingAnalysis } from '../services/analysisService';

const HISTORY_STORAGE_KEY = 'satquery_analysis_history';
const SETTINGS_STORAGE_KEY = 'satquery_user_settings';

const defaultSettings: UserSettings = {
  theme: 'dark',
  language: 'en',
  defaultMode: 'single',
  autoSelectWorkflow: true,
  confidenceThreshold: 0.8,
  showTraceByDefault: false,
  showVisualEvidence: true,
  showEvidenceOverlays: true,
  showExecutionTrace: true,
  mockSimulatedLatencyMs: 1200,
  showMockBanner: true,
};

const initialDefaultFiles: UploadedFileState[] = [
  {
    file: new File(['mock-optical'], 'cartosat2s_visakhapatnam_optical.tif', { type: 'image/tiff' }),
    id: 'preset-opt-01',
    name: 'cartosat2s_visakhapatnam_optical.tif',
    size: 14200000,
    type: 'GeoTIFF',
    previewUrl: SAMPLE_OPTICAL_PORT,
    modality: 'optical',
    role: 'before',
    acquisitionDate: '2024-01-15T09:30:00Z',
    progress: 100,
    uploaded: true,
    metadata: {
      bands: 4,
      crs: 'EPSG:32644',
      resolution: 0.6,
      width: 600,
      height: 600,
      sensor: 'Cartosat-2S PAN/MX',
      satellite: 'Cartosat-2S',
    },
  },
];

const loadSavedHistory = (): HistoryRecord[] => {
  try {
    const saved = localStorage.getItem(HISTORY_STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
};

const loadSavedSettings = (): UserSettings => {
  try {
    const saved = localStorage.getItem(SETTINGS_STORAGE_KEY);
    return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
  } catch {
    return defaultSettings;
  }
};

interface AppState {
  workflowMode: AppWorkflowMode;
  files: UploadedFileState[];
  activePresetId: string | null;
  query: string;
  isAnalyzing: boolean;
  analysisStepText: string;
  currentResult: EngineResult | null;
  currentJobId: string | null;
  chatMessages: ChatMessage[];
  history: HistoryRecord[];
  
  // Viewer state
  viewerLayer: 'original' | 'evidence' | 'change_mask' | 'segmentation' | 'grounding';
  crossModalActiveLayer: 'optical' | 'sar';
  temporalSwipePosition: number; // 0 - 100 %
  isTraceOpen: boolean;
  selectedBoundingBox: BoundingBox | null;
  userSettings: UserSettings;

  // Actions
  setWorkflowMode: (mode: AppWorkflowMode) => void;
  addFiles: (newFiles: File[]) => void;
  removeFile: (id: string) => void;
  updateFileRole: (id: string, role: Role) => void;
  updateFileModality: (id: string, modality: Modality) => void;
  loadPreset: (preset: SampleDataset) => void;
  setQuery: (query: string) => void;
  runAnalysis: (customQuery?: string) => Promise<void>;
  resetAnalysis: () => void;
  setViewerLayer: (layer: AppState['viewerLayer']) => void;
  setCrossModalLayer: (modality: 'optical' | 'sar') => void;
  setTemporalSwipePosition: (pos: number) => void;
  toggleTraceOpen: () => void;
  setSelectedBoundingBox: (box: BoundingBox | null) => void;
  clearHistory: () => void;
  updateSettings: (newSettings: Partial<UserSettings>) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  workflowMode: 'single',
  files: initialDefaultFiles,
  activePresetId: 'isro-cartosat-coastal-port',
  query: '',
  isAnalyzing: false,
  analysisStepText: '',
  currentResult: null,
  currentJobId: null,
  chatMessages: [
    {
      id: 'welcome-1',
      sender: 'agent',
      content: '🛰️ Welcome to SatQuery AI! Upload single, bi-temporal, or optical+SAR imagery and ask questions in natural language. The agentic system will automatically route, validate, and execute the appropriate specialist remote sensing workflow.',
      timestamp: new Date().toISOString(),
    },
  ],
  history: loadSavedHistory(),
  viewerLayer: 'evidence',
  crossModalActiveLayer: 'optical',
  temporalSwipePosition: 50,
  isTraceOpen: false,
  selectedBoundingBox: null,
  userSettings: loadSavedSettings(),

  setWorkflowMode: (mode) => {
    set({ workflowMode: mode, currentResult: null });
  },

  addFiles: (newFiles) => {
    const current = get().files;
    if (current.length + newFiles.length > 2) {
      alert('Maximum 2 satellite images allowed per analysis session.');
      return;
    }

    const created = newFiles.map((file, idx) => {
      const isOptical = !file.name.toLowerCase().includes('sar');
      return {
        file,
        id: 'file-' + Math.random().toString(36).substring(2, 9),
        name: file.name,
        size: file.size,
        type: file.name.endsWith('.tif') || file.name.endsWith('.tiff') ? 'GeoTIFF' : 'Image',
        previewUrl: URL.createObjectURL(file),
        modality: (isOptical ? 'optical' : 'sar') as Modality,
        role: (idx === 0 ? 'before' : 'after') as Role,
        acquisitionDate: new Date().toISOString().split('T')[0],
        progress: 100,
        uploaded: true,
        metadata: {
          bands: isOptical ? 4 : 2,
          crs: 'EPSG:4326',
          resolution: 1.0,
          width: 600,
          height: 600,
          sensor: isOptical ? 'Optical VNIR' : 'C-Band SAR',
          satellite: isOptical ? 'Cartosat/Sentinel-2' : 'RISAT/Sentinel-1',
        },
      };
    });

    set({ files: [...current, ...created], activePresetId: null });
  },

  removeFile: (id) => {
    const updated = get().files.filter((f) => f.id !== id);
    set({ files: updated });
  },

  updateFileRole: (id, role) => {
    const updated = get().files.map((f) => (f.id === id ? { ...f, role } : f));
    set({ files: updated });
  },

  updateFileModality: (id, modality) => {
    const updated = get().files.map((f) => (f.id === id ? { ...f, modality } : f));
    set({ files: updated });
  },

  loadPreset: (preset) => {
    const loadedFiles: UploadedFileState[] = preset.images.map((img, idx) => ({
      file: new File(['preset-blob'], img.name, { type: 'image/tiff' }),
      id: `preset-${preset.id}-${idx}`,
      name: img.name,
      size: 15400000,
      type: 'GeoTIFF',
      previewUrl: img.previewUrl,
      modality: img.modality,
      role: img.role || (idx === 0 ? 'before' : 'after'),
      acquisitionDate: img.acquisitionDate || '2024-01-15',
      progress: 100,
      uploaded: true,
      metadata: img.metadata,
    }));

    set({
      workflowMode: preset.mode,
      files: loadedFiles,
      activePresetId: preset.id,
      query: preset.recommendedQueries[0] || '',
      currentResult: null,
      viewerLayer: 'evidence',
    });
  },

  setQuery: (query) => set({ query }),

  runAnalysis: async (customQuery) => {
    const { files, query: storeQuery, userSettings, history } = get();
    const activeQuery = customQuery || storeQuery;

    if (!activeQuery || activeQuery.trim().length === 0) return;
    if (files.length === 0) {
      alert('Please upload or select at least one satellite image.');
      return;
    }

    // Add user message to chat
    const userMsg: ChatMessage = {
      id: 'msg-' + Date.now(),
      sender: 'user',
      content: activeQuery,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      isAnalyzing: true,
      analysisStepText: 'Analyzing request...',
      chatMessages: [...state.chatMessages, userMsg],
    }));

    try {
      const result = await executeRemoteSensingAnalysis({
        query: activeQuery,
        files,
        latencyMs: userSettings.mockSimulatedLatencyMs,
        onProgress: (status) => set({ analysisStepText: status }),
      });

      const agentMsg: ChatMessage = {
        id: 'agent-' + Date.now(),
        sender: 'agent',
        content: result.answer || (result.errors.length > 0 ? result.errors[0].message : 'Analysis completed.'),
        timestamp: new Date().toISOString(),
        result,
      };

      // Save to history
      const newHistoryRecord: HistoryRecord = {
        id: 'hist-' + Date.now(),
        jobId: result.request_id,
        date: new Date().toISOString(),
        taskType: result.task || ('single_image_vqa' as TaskType),
        inputMode: get().workflowMode,
        query: activeQuery,
        confidence: result.confidence,
        status: result.status === 'success' ? 'completed' : 'failed',
        answerSummary: result.answer || 'Analysis error',
        imagePreviews: files.map((f) => f.previewUrl),
        engineResult: result,
      };

      const updatedHistory = [newHistoryRecord, ...history].slice(0, 25);
      try {
        localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updatedHistory));
      } catch (e) {
        console.warn('Could not save history to localStorage', e);
      }

      set((state) => ({
        isAnalyzing: false,
        analysisStepText: '',
        currentResult: result,
        chatMessages: [...state.chatMessages, agentMsg],
        history: updatedHistory,
      }));
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: 'err-' + Date.now(),
        sender: 'system',
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString(),
      };
      set((state) => ({
        isAnalyzing: false,
        analysisStepText: '',
        chatMessages: [...state.chatMessages, errorMsg],
      }));
    }
  },

  resetAnalysis: () => {
    set({
      currentResult: null,
      query: '',
      selectedBoundingBox: null,
    });
  },

  setViewerLayer: (layer) => set({ viewerLayer: layer }),
  setCrossModalLayer: (modality) => set({ crossModalActiveLayer: modality }),
  setTemporalSwipePosition: (pos) => set({ temporalSwipePosition: pos }),
  toggleTraceOpen: () => set((state) => ({ isTraceOpen: !state.isTraceOpen })),
  setSelectedBoundingBox: (box) => set({ selectedBoundingBox: box }),

  clearHistory: () => {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
    set({ history: [] });
  },

  updateSettings: (newSettings) => {
    const updated = { ...get().userSettings, ...newSettings };
    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(updated));
    set({ userSettings: updated });
  },
}));
