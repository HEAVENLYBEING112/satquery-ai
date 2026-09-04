// frontend/src/api/mock/mockData.ts
import { EngineResult, CapabilitiesResponse, HealthResponse } from '../../types/engine';
import { SampleDataset } from '../../types/app';

// 1. High-fidelity SVGs embedded as Data URLs for immediate rendering
export const SAMPLE_OPTICAL_PORT = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="%231a365d"/>
  <!-- Sea / Water -->
  <path d="M0 0 L420 0 L320 600 L0 600 Z" fill="%230c4a6e"/>
  <path d="M0 100 Q 150 120 300 90 T 400 300 L 350 600 L 0 600 Z" fill="%230369a1" opacity="0.4"/>
  <!-- Land / Urban -->
  <path d="M420 0 L600 0 L600 600 L320 600 Z" fill="%23334155"/>
  <!-- Vegetated Area -->
  <polygon points="450,50 580,30 570,180 430,120" fill="%23166534" opacity="0.8"/>
  <polygon points="480,420 590,400 580,570 410,550" fill="%2314532d" opacity="0.75"/>
  <!-- Industrial / Port Berths & Docks -->
  <rect x="330" y="150" width="120" height="25" fill="%2394a3b8" rx="2"/>
  <rect x="310" y="220" width="150" height="28" fill="%2394a3b8" rx="2"/>
  <rect x="290" y="300" width="160" height="30" fill="%2394a3b8" rx="2"/>
  <rect x="280" y="380" width="140" height="25" fill="%2394a3b8" rx="2"/>
  <!-- Ships / Cargo Vessels -->
  <path d="M220 225 L290 222 L300 234 L290 246 L220 243 Z" fill="%23e2e8f0"/>
  <circle cx="250" cy="234" r="4" fill="%23ef4444"/>
  <path d="M180 305 L260 302 L270 315 L260 328 L180 325 Z" fill="%23f8fafc"/>
  <circle cx="220" cy="315" r="4" fill="%233b82f6"/>
  <!-- Urban Grid -->
  <rect x="460" y="200" width="40" height="30" fill="%2364748b"/>
  <rect x="520" y="200" width="50" height="30" fill="%23475569"/>
  <rect x="460" y="250" width="50" height="40" fill="%23475569"/>
  <rect x="530" y="250" width="40" height="40" fill="%2364748b"/>
  <rect x="460" y="310" width="110" height="50" fill="%23334155" stroke="%2364748b" stroke-width="2"/>
  <!-- Satellite Grid Lines -->
  <line x1="0" y1="200" x2="600" y2="200" stroke="%2338bdf8" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.4"/>
  <line x1="0" y1="400" x2="600" y2="400" stroke="%2338bdf8" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.4"/>
  <line x1="200" y1="0" x2="200" y2="600" stroke="%2338bdf8" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.4"/>
  <line x1="400" y1="0" x2="400" y2="600" stroke="%2338bdf8" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.4"/>
  <text x="20" y="40" fill="%2338bdf8" font-family="monospace" font-size="14" font-weight="bold">SYNTHETIC MOCK-SAT OPTICAL RGB (10m GSD)</text>
</svg>`;

export const SAMPLE_SAR_PORT = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="%23020617"/>
  <!-- Water specular reflection: pure dark in SAR -->
  <path d="M0 0 L420 0 L320 600 L0 600 Z" fill="%23050b14"/>
  <!-- Land backscatter (speckled gray texture) -->
  <path d="M420 0 L600 0 L600 600 L320 600 Z" fill="%2327272a"/>
  <!-- High metallic double-bounce backscatter (Docks & Berths: very bright white) -->
  <rect x="330" y="150" width="120" height="25" fill="%23ffffff" filter="drop-shadow(0 0 4px %23ffffff)"/>
  <rect x="310" y="220" width="150" height="28" fill="%23ffffff" filter="drop-shadow(0 0 4px %23ffffff)"/>
  <rect x="290" y="300" width="160" height="30" fill="%23ffffff" filter="drop-shadow(0 0 4px %23ffffff)"/>
  <rect x="280" y="380" width="140" height="25" fill="%23ffffff" filter="drop-shadow(0 0 4px %23ffffff)"/>
  <!-- Ships: extreme dihedral bright points in dark water -->
  <polygon points="220,234 290,222 300,234 290,246" fill="%23ffffff" filter="drop-shadow(0 0 8px %23ffffff)"/>
  <polygon points="180,315 260,302 270,315 260,328" fill="%23ffffff" filter="drop-shadow(0 0 8px %23ffffff)"/>
  <!-- Urban building corners: bright scatter points -->
  <circle cx="480" cy="215" r="5" fill="%23e4e4e7"/>
  <circle cx="540" cy="215" r="6" fill="%23ffffff"/>
  <circle cx="485" cy="270" r="5" fill="%23e4e4e7"/>
  <circle cx="550" cy="270" r="7" fill="%23ffffff"/>
  <circle cx="515" cy="335" r="8" fill="%23ffffff"/>
  <text x="20" y="40" fill="%23fbbf24" font-family="monospace" font-size="14" font-weight="bold">SYNTHETIC MOCK-SAT SAR C-BAND</text>
</svg>`;

export const SAMPLE_TEMPORAL_T1 = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="%231e293b"/>
  <!-- River Basin T1 (Pre-Monsoon / Normal) -->
  <path d="M 0 260 Q 200 240 350 320 T 600 280 L 600 340 Q 350 380 200 300 T 0 320 Z" fill="%230284c7"/>
  <!-- Agricultural Green Fields -->
  <rect x="50" y="50" width="180" height="150" fill="%2315803d" rx="4"/>
  <rect x="260" y="40" width="200" height="160" fill="%2316a34a" rx="4"/>
  <rect x="80" y="380" width="220" height="170" fill="%2322c55e" rx="4"/>
  <rect x="330" y="400" width="220" height="150" fill="%2315803d" rx="4"/>
  <!-- Urban Settlement -->
  <rect x="480" y="60" width="80" height="80" fill="%2364748b"/>
  <text x="20" y="40" fill="%2338bdf8" font-family="monospace" font-size="14" font-weight="bold">DATE 1: 2024-01-15 (T1 - PRE-MONSOON)</text>
</svg>`;

export const SAMPLE_TEMPORAL_T2 = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="%231e293b"/>
  <!-- River Inundation T2 (Post-Monsoon Flood Expansion) -->
  <path d="M 0 160 Q 200 120 350 220 T 600 180 L 600 460 Q 350 500 200 420 T 0 440 Z" fill="%230369a1"/>
  <!-- Submerged & Inundated Zones -->
  <rect x="50" y="50" width="180" height="150" fill="%23075985" opacity="0.85" rx="4"/>
  <rect x="260" y="40" width="200" height="160" fill="%230369a1" opacity="0.9" rx="4"/>
  <rect x="80" y="380" width="220" height="170" fill="%230284c7" opacity="0.8" rx="4"/>
  <!-- Remaining Land -->
  <rect x="330" y="420" width="220" height="130" fill="%23854d0e" rx="4"/>
  <rect x="480" y="60" width="80" height="80" fill="%23475569"/>
  <text x="20" y="40" fill="%23ef4444" font-family="monospace" font-size="14" font-weight="bold">DATE 2: 2024-08-10 (T2 - POST-MONSOON INUNDATION)</text>
</svg>`;

export const SAMPLE_CHANGE_MASK = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="transparent"/>
  <!-- Inundated Delta Change Region highlighted in Red/Magenta -->
  <path d="M 0 160 Q 200 120 350 220 T 600 180 L 600 280 Q 350 320 200 240 T 0 260 Z" fill="%23ef4444" opacity="0.65"/>
  <path d="M 0 320 Q 200 300 350 380 T 600 340 L 600 460 Q 350 500 200 420 T 0 440 Z" fill="%23f43f5e" opacity="0.7"/>
  <rect x="50" y="100" width="180" height="100" fill="%23dc2626" opacity="0.6"/>
</svg>`;

// 2. Deterministic Engine Fixtures strictly adhering to SRS Section 34.2
export const MOCK_VQA_RESULT: EngineResult = {
  request_id: 'vqa-550e8400-e29b-41d4-a716-446655440001',
  status: 'success',
  query: 'What is visible in this satellite scene?',
  task: 'single_image_vqa',
  answer: 'The satellite image shows a deep-water coastal port with industrial docking piers, maritime cargo vessels anchored along the jetty, dense urban infrastructure in the north-east, and peripheral vegetation cover.',
  confidence: null, // SRS Rule: Mock models and baseline VQA return confidence=null
  specialist_results: [
    {
      status: 'success',
      model_name: 'remote_sensing_vqa',
      task: 'single_image_vqa',
      answer: 'Deep-water coastal port facility with cargo vessels, berthing jetties, and adjacent mixed urban/vegetation zones.',
      confidence: null,
      evidence: {
        textual_evidence: 'Identified coastal waterbody (45% scene coverage), industrial maritime infrastructure (22%), urban built-up (20%), and dense canopy vegetation (13%).',
        bounding_boxes: [],
        visualizations: ['/samples/optical_port.png'],
        change_statistics: null,
        change_mask: null,
        metadata: {
          sensor: 'Synthetic RGB',
          ground_sample_distance_m: 0.6,
          spectral_bands: ['Red', 'Green', 'Blue', 'NIR'],
        },
      },
      metadata: {},
      execution_time: 1.12,
      error: null,
    },
  ],
  evidence: [
    {
      textual_evidence: 'Identified coastal waterbody (45% scene coverage), industrial maritime infrastructure (22%), urban built-up (20%), and dense canopy vegetation (13%).',
      bounding_boxes: [],
      visualizations: ['/samples/optical_port.png'],
      change_statistics: null,
      change_mask: null,
      metadata: {
        sensor: 'Synthetic RGB',
        ground_sample_distance_m: 0.6,
      },
    },
  ],
  execution_trace: [
    {
      step: 1,
      tool: 'remote_sensing_vqa',
      task: 'single_image_vqa',
      status: 'success',
      parameters: { prompt: 'What is visible in this satellite scene?', top_k: 5 },
      duration_ms: 1120,
      result_summary: 'Identified deep-water port, berths, vessels, urban, and vegetation.',
    },
  ],
  errors: [],
};

export const MOCK_GROUNDING_RESULT: EngineResult = {
  request_id: 'grd-550e8400-e29b-41d4-a716-446655440002',
  status: 'success',
  query: 'Highlight the cargo vessels and docking piers',
  task: 'single_image_grounding',
  answer: 'Located 2 major cargo transport vessels anchored at maritime berths and 4 industrial pier structures extending into the channel.',
  confidence: null,
  specialist_results: [
    {
      status: 'success',
      model_name: 'remote_sensing_grounding',
      task: 'single_image_grounding',
      answer: 'Grounded 6 target objects in pixel space matching queries [cargo vessels, docking piers].',
      confidence: null,
      evidence: {
        textual_evidence: 'Spatial grounding identified 2 vessels in active berth positions and 4 structural concrete piers.',
        bounding_boxes: [
          {
            label: 'cargo_vessel_primary',
            coordinates: [180, 290, 305, 340],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'model',
          },
          {
            label: 'cargo_vessel_secondary',
            coordinates: [210, 210, 310, 255],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'model',
          },
          {
            label: 'docking_pier_alpha',
            coordinates: [280, 140, 460, 185],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'model',
          },
          {
            label: 'docking_pier_beta',
            coordinates: [270, 210, 470, 260],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'model',
          },
        ],
        visualizations: ['/samples/optical_port.png'],
        change_statistics: null,
        change_mask: null,
        metadata: {},
      },
      metadata: {},
      execution_time: 1.45,
      error: null,
    },
  ],
  evidence: [
    {
      textual_evidence: 'Spatial grounding identified 2 vessels in active berth positions and 4 structural concrete piers.',
      bounding_boxes: [
        {
          label: 'cargo_vessel_primary',
          coordinates: [180, 290, 305, 340],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'model',
        },
        {
          label: 'cargo_vessel_secondary',
          coordinates: [210, 210, 310, 255],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'model',
        },
        {
          label: 'docking_pier_alpha',
          coordinates: [280, 140, 460, 185],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'model',
        },
        {
          label: 'docking_pier_beta',
          coordinates: [270, 210, 470, 260],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'model',
        },
      ],
      visualizations: ['/samples/optical_port.png'],
      change_statistics: null,
      change_mask: null,
      metadata: {},
    },
  ],
  execution_trace: [
    {
      step: 1,
      tool: 'remote_sensing_grounding',
      task: 'single_image_grounding',
      status: 'success',
      parameters: { query: 'cargo vessels and docking piers', nms_threshold: 0.45 },
      duration_ms: 1450,
      result_summary: 'Extracted 4 bounding boxes with coordinate_type=pixel.',
    },
  ],
  errors: [],
};

export const MOCK_TEMPORAL_RESULT: EngineResult = {
  request_id: 'tmp-550e8400-e29b-41d4-a716-446655440003',
  status: 'success',
  query: 'What changed between these two dates and where did the change occur?',
  task: 'temporal_change_description',
  answer: 'The analysis detected significant hydrologic expansion between 2024-01-15 and 2024-08-10. Extreme river channel inundation submerged 12.4% of previously cultivated agricultural zones in the central and north-western floodplain.',
  confidence: null,
  specialist_results: [
    {
      status: 'success',
      model_name: 'baseline_change_detector',
      task: 'temporal_change_detection',
      answer: '3 major changed inundation clusters detected across 1,247 pixels.',
      confidence: null,
      evidence: {
        textual_evidence: 'Bi-temporal difference analysis completed using thresholded band ratioing (NDWI difference).',
        bounding_boxes: [
          {
            label: 'inundated_agricultural_zone',
            coordinates: [40, 90, 250, 220],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'baseline_change_detector',
          },
          {
            label: 'floodplain_channel_widening',
            coordinates: [0, 160, 600, 460],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'baseline_change_detector',
          },
        ],
        visualizations: ['/samples/temporal_t1.png', '/samples/temporal_t2.png'],
        change_statistics: {
          changed_pixels: 1247,
          changed_fraction: 0.124,
          threshold_used: 0.2,
          built_up_change: '+1.2%',
          vegetation_loss: '-12.4%',
          water_expansion: '+18.6%',
        },
        change_mask: {
          width: 600,
          height: 600,
          mask_url: SAMPLE_CHANGE_MASK,
          threshold_used: 0.2,
          changed_pixel_count: 1247,
          changed_fraction: 0.124,
        },
        metadata: {},
      },
      metadata: {},
      execution_time: 0.412,
      error: null,
    },
    {
      status: 'success',
      model_name: 'mock_change_description',
      task: 'temporal_change_description',
      answer: 'Synthesized bi-temporal narrative: Severe monsoon inundation across riverine floodplains.',
      confidence: null,
      evidence: {
        textual_evidence: 'Vegetation indices dropped sharply in inundated parcels while NDWI surged by 0.48.',
        bounding_boxes: [],
        visualizations: [],
        change_statistics: null,
        change_mask: null,
        metadata: {},
      },
      metadata: {},
      execution_time: 0.088,
      error: null,
    },
  ],
  evidence: [
    {
      textual_evidence: 'Vegetation indices dropped sharply in inundated parcels while NDWI surged by 0.48.',
      bounding_boxes: [
        {
          label: 'inundated_agricultural_zone',
          coordinates: [40, 90, 250, 220],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'baseline_change_detector',
        },
        {
          label: 'floodplain_channel_widening',
          coordinates: [0, 160, 600, 460],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'baseline_change_detector',
        },
      ],
      visualizations: ['/samples/temporal_t1.png', '/samples/temporal_t2.png'],
      change_statistics: {
        changed_pixels: 1247,
        changed_fraction: 0.124,
        threshold_used: 0.2,
        built_up_change: '+1.2%',
        vegetation_loss: '-12.4%',
        water_expansion: '+18.6%',
      },
      change_mask: {
        width: 600,
        height: 600,
        mask_url: SAMPLE_CHANGE_MASK,
        threshold_used: 0.2,
        changed_pixel_count: 1247,
        changed_fraction: 0.124,
      },
      metadata: {},
    },
  ],
  execution_trace: [
    {
      step: 1,
      tool: 'baseline_change_detector',
      task: 'temporal_change_detection',
      status: 'success',
      parameters: { threshold: 0.2, method: 'siamese_ndwi_diff' },
      duration_ms: 412,
      result_summary: 'Detected 3 changed regions (1,247 pixels, 12.4% scene fraction).',
    },
    {
      step: 2,
      tool: 'mock_change_description',
      task: 'temporal_change_description',
      status: 'success',
      parameters: { change_statistics: { changed_pixels: 1247 } },
      duration_ms: 88,
      result_summary: 'Synthesized change description for flood analysis.',
    },
  ],
  errors: [],
};

export const MOCK_CROSSMODAL_RESULT: EngineResult = {
  request_id: 'xmod-550e8400-e29b-41d4-a716-446655440004',
  status: 'success',
  query: 'Classify using SAR and optical images together',
  task: 'cross_modal_optical_sar',
  answer: 'Cross-modal synergy verified: Optical imagery provides spectral land-cover differentiation while SAR backscatter confirms solid built structures and penetrates through cloud artifacts, confirming 94% water boundary consensus.',
  confidence: null,
  specialist_results: [
    {
      status: 'success',
      model_name: 'OpticalSARSpecialist',
      task: 'cross_modal_optical_sar',
      answer: 'Deterministic Optical-SAR feature extraction complete with mutual agreement bounding boxes.',
      confidence: null,
      evidence: {
        textual_evidence: 'High SAR backscatter corroborated concrete port structures, while optical NIR confirmed water boundaries.',
        bounding_boxes: [
          {
            label: 'water_agreement',
            coordinates: [10, 10, 360, 580],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'cross_modal',
          },
          {
            label: 'built_agreement',
            coordinates: [340, 140, 580, 580],
            coordinate_type: 'pixel',
            confidence: null,
            source: 'cross_modal',
          },
        ],
        visualizations: ['/samples/optical_port.png', '/samples/sar_port.png'],
        change_statistics: {
          optical_water_pixels: 38400,
          sar_water_pixels: 39120,
          water_agreement_pixels: 37950,
          water_disagreement_pixels: 1170,
          concordance_rate: '97.0%',
        },
        change_mask: null,
        metadata: {
          fallback_triggered: true,
          fallback_reason: 'CROMA hardware/dependencies unavailable (Running calibrated deterministic OpticalSARSpecialist fallback).',
        },
      },
      metadata: {
        fallback_triggered: true,
        fallback_reason: 'CROMA hardware/dependencies unavailable',
      },
      execution_time: 0.654,
      error: null,
    },
  ],
  evidence: [
    {
      textual_evidence: 'High SAR backscatter corroborated concrete port structures, while optical NIR confirmed water boundaries.',
      bounding_boxes: [
        {
          label: 'water_agreement',
          coordinates: [10, 10, 360, 580],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'cross_modal',
        },
        {
          label: 'built_agreement',
          coordinates: [340, 140, 580, 580],
          coordinate_type: 'pixel',
          confidence: null,
          source: 'cross_modal',
        },
      ],
      visualizations: ['/samples/optical_port.png', '/samples/sar_port.png'],
      change_statistics: {
        optical_water_pixels: 38400,
        sar_water_pixels: 39120,
        water_agreement_pixels: 37950,
        water_disagreement_pixels: 1170,
        concordance_rate: '97.0%',
      },
      change_mask: null,
      metadata: {
        fallback_triggered: true,
        fallback_reason: 'CROMA hardware/dependencies unavailable (Running calibrated deterministic OpticalSARSpecialist fallback).',
      },
    },
  ],
  execution_trace: [
    {
      step: 1,
      tool: 'OpticalSARSpecialist',
      task: 'cross_modal_optical_sar',
      status: 'success',
      parameters: { co_registration: 'verified', bands: ['optical_rgb', 'sar_vv_vh'] },
      duration_ms: 654,
      result_summary: 'Extracted cross-modal consensus with 97.0% spatial agreement.',
    },
  ],
  errors: [],
};

export const MOCK_FAILED_RESULT: EngineResult = {
  request_id: 'err-550e8400-e29b-41d4-a716-446655440005',
  status: 'failed',
  query: 'Compare the change over time',
  task: null,
  answer: null,
  confidence: null,
  specialist_results: [],
  evidence: [],
  execution_trace: [],
  errors: [
    {
      code: 'PLANNING_FAILED',
      message: 'Temporal change query received, but only 1 image asset was provided. Bi-temporal change workflows require 2 co-registered images (T1 Before, T2 After).',
    },
  ],
};

// // 3. Preset Satellite Datasets for UI Demonstrations
export const SAMPLE_DATASETS: SampleDataset[] = [
  {
    id: 'synthetic-coastal-port',
    title: 'Synthetic Port Infrastructure',
    subtitle: 'Local Synthetic Optical & SAR Fixture Pair',
    description: 'Co-registered synthetic optical and SAR test fixtures for zero-budget UI demonstration.',
    mode: 'cross_modal',
    badge: 'Demo Fixture',
    recommendedQueries: [
      'Describe the land-cover and major objects visible in this image.',
      'Highlight the cargo vessels and docking piers',
      'Classify using SAR and optical images together',
      'Identify built-up and water-covered regions.',
    ],
    images: [
      {
        name: 'synthetic_optical.tif',
        previewUrl: SAMPLE_OPTICAL_PORT,
        fileUrl: '/samples/cartosat_synthetic.tif',
        modality: 'optical',
        metadata: {
          bands: 3,
          crs: 'EPSG:32610 (UTM Zone 10N)',
          resolution: 10.0,
          width: 256,
          height: 256,
          sensor: 'Synthetic RGB',
          satellite: 'Mock-Sat',
        },
      },
      {
        name: 'synthetic_sar.tif',
        previewUrl: SAMPLE_SAR_PORT,
        fileUrl: '/samples/risat_synthetic.tif',
        modality: 'sar',
        role: 'after',
        metadata: {
          bands: 1,
          crs: 'EPSG:32610 (UTM Zone 10N)',
          resolution: 10.0,
          width: 256,
          height: 256,
          sensor: 'Synthetic C-Band',
          satellite: 'Mock-Sat',
        },
      },
    ],
  },
  {
    id: 'synthetic-flood-temporal',
    title: 'Synthetic Flood Plain Change',
    subtitle: 'Bi-Temporal Synthetic Flood Monitoring',
    description: 'Multi-date seasonal comparison before and after monsoon flood wave inundation (synthetic fixture).',
    mode: 'temporal',
    badge: 'Disaster Management',
    recommendedQueries: [
      'What changed between these two dates and where did the change occur?',
      'Has the water-covered area increased, decreased, or remained unchanged?',
      'Describe the changes in agricultural land.',
      'Highlight the inundated zones.',
    ],
    images: [
      {
        name: 'synthetic_t1.tif',
        previewUrl: SAMPLE_TEMPORAL_T1,
        fileUrl: '/samples/synthetic_before.tif',
        modality: 'optical',
        role: 'before',
        acquisitionDate: '2024-01-15',
        metadata: {
          bands: 3,
          crs: 'EPSG:32610 (UTM Zone 10N)',
          resolution: 10.0,
          width: 256,
          height: 256,
          sensor: 'Synthetic Optical',
          satellite: 'Mock-Sat',
        },
      },
      {
        name: 'synthetic_t2.tif',
        previewUrl: SAMPLE_TEMPORAL_T2,
        fileUrl: '/samples/synthetic_after.tif',
        modality: 'optical',
        role: 'after',
        acquisitionDate: '2024-08-10',
        metadata: {
          bands: 3,
          crs: 'EPSG:32610 (UTM Zone 10N)',
          resolution: 10.0,
          width: 256,
          height: 256,
          sensor: 'Synthetic Optical',
          satellite: 'Mock-Sat',
        },
      },
    ],
  },
  {
    id: 'synthetic-urban-growth',
    title: 'Synthetic Urban Growth Corridors',
    subtitle: 'Single Optical Scene with High-Density Grounding',
    description: 'High-density urban area for land use classification (synthetic fixture).',
    mode: 'single',
    badge: 'Urban Planning',
    recommendedQueries: [
      'What land cover is visible in this image?',
      'Highlight the built-up structures and transit corridors.',
      'Estimate the vegetation canopy percentage.',
      'Describe this scene in detail.',
    ],
    images: [
      {
        name: 'synthetic_urban_optical.tif',
        previewUrl: SAMPLE_OPTICAL_PORT,
        fileUrl: '/samples/cartosat_synthetic.tif',
        modality: 'optical',
        metadata: {
          bands: 3,
          crs: 'EPSG:32610 (UTM Zone 10N)',
          resolution: 10.0,
          width: 256,
          height: 256,
          sensor: 'Synthetic Optical',
          satellite: 'Mock-Sat',
        },
      },
    ],
  },
];

export const MOCK_CAPABILITIES: CapabilitiesResponse = {
  tasks: [
    'single_image_vqa',
    'single_image_caption',
    'single_image_grounding',
    'temporal_change_detection',
    'temporal_change_description',
    'temporal_change_vqa',
    'cross_modal_optical_sar',
    'croma_classification',
  ],
  input_types: [
    'single_optical',
    'single_multispectral',
    'single_sar',
    'temporal_optical',
    'temporal_sar',
    'optical_sar_pair',
  ],
  supported_formats: ['GeoTIFF', 'TIFF', 'PNG', 'JPEG'],
  max_upload_bytes: 52428800, // 50MB
  models: {
    mock: [
      'MockVQA',
      'MockGrounding',
      'MockCaptioner',
      'baseline_change_detector',
      'OpticalSARSpecialist',
    ],
    real: [
      'remote_sensing_vqa',
      'remote_sensing_grounding',
      'croma_specialist',
      'ChangeFormer_V2',
    ],
  },
};

export const MOCK_HEALTH: HealthResponse = {
  status: 'healthy',
  version: '2.0.0-SAC',
  engine_mode: 'mock',
  timestamp: new Date().toISOString(),
};
