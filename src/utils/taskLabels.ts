// frontend/src/utils/taskLabels.ts
import { TaskType, InputType, Modality } from '../types/engine';

export const TASK_LABELS: Record<TaskType, { title: string; category: string; description: string; badgeColor: string }> = {
  single_image_vqa: {
    title: 'Visual Question Answering',
    category: 'Single Image',
    description: 'Natural language question answering over remote sensing imagery.',
    badgeColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  },
  single_image_caption: {
    title: 'Scene Captioning',
    category: 'Single Image',
    description: 'Comprehensive descriptive summary of land use, objects, and environment.',
    badgeColor: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  },
  single_image_grounding: {
    title: 'Region Grounding',
    category: 'Single Image',
    description: 'Text-guided localization and bounding box extraction for targets.',
    badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  },
  temporal_change_detection: {
    title: 'Temporal Change Detection',
    category: 'Bi-Temporal',
    description: 'Pixel-level statistical and binary change map generation across two dates.',
    badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  },
  temporal_change_description: {
    title: 'Temporal Change Description',
    category: 'Bi-Temporal',
    description: 'Narrative description of what transformed between before and after observations.',
    badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  },
  temporal_change_vqa: {
    title: 'Change-based VQA (CDVQA)',
    category: 'Bi-Temporal',
    description: 'Answers complex questions comparing multi-date satellite scenes.',
    badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  },
  cross_modal_optical_sar: {
    title: 'Optical + SAR Fusion',
    category: 'Cross-Modal',
    description: 'Joint extraction combining optical spectral bands with radar backscatter.',
    badgeColor: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  },
  croma_classification: {
    title: 'CROMA Multimodal Classifier',
    category: 'Cross-Modal',
    description: 'Contrastive Optical+SAR representation alignment for robust classification.',
    badgeColor: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
  },
};

export const INPUT_TYPE_LABELS: Record<InputType, string> = {
  single_optical: 'Single Optical / Multispectral',
  single_multispectral: 'Single Multispectral Band Stack',
  single_sar: 'Single SAR Radar (C/L-Band)',
  temporal_optical: 'Bi-Temporal Optical Pair (T1 / T2)',
  temporal_sar: 'Bi-Temporal SAR Pair (T1 / T2)',
  optical_sar_pair: 'Co-registered Optical + SAR Pair',
};

export const MODALITY_INFO: Record<Modality, { name: string; description: string; sensorExample: string; color: string }> = {
  optical: {
    name: 'Optical / Multispectral',
    description: 'Captures spectral reflectance, visible RGB, NIR, Red-Edge, and NDVI indices.',
    sensorExample: 'Cartosat-2S / Sentinel-2 / Landsat-8/9',
    color: 'text-sky-400 border-sky-500/30 bg-sky-500/10',
  },
  sar: {
    name: 'Synthetic Aperture Radar (SAR)',
    description: 'Active radar sensor penetrating clouds, haze, and night. Provides surface roughness & backscatter (VV/VH).',
    sensorExample: 'RISAT-1A / EOS-04 / Sentinel-1',
    color: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
  },
};
