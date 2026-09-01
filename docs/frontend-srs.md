# SatQuery AI — Frontend Master Software Requirements Specification

## Title Page
**Project**: SatQuery AI  
**Document**: Frontend Master Software Requirements Specification (SRS)  
**Version**: 1.0  
**Target**: National-Level Hackathon (Smart India Hackathon)  
**Engine Status**: Engine V1 (FROZEN)

---

## 1. Executive Summary
SatQuery AI is an advanced natural-language remote-sensing analysis system designed for the Smart India Hackathon. It enables users to upload remote sensing imagery (optical, SAR, or temporal pairs) and query them using natural language. The backend computation layer (Engine V1) has been completely stabilized and frozen. This document serves as the absolute, standalone specification for implementing the React/Next.js frontend interface that will consume the backend API.

## 2. Scope
This SRS dictates all frontend behavior. The frontend must act purely as a presentation and interaction layer. It must orchestrate file uploads, query submissions, job polling, result rendering, and evidence visualization. The frontend is forbidden from performing geospatial analytics or AI inference itself, ensuring strict separation of concerns.

## 3. Objectives
- Provide a hackathon-ready frontend that works on low-spec developer machines.
- Render high-fidelity geospatial evidence natively.
- Enforce scientific honesty through UI constraints (e.g., handling missing confidences, visualizing AI fallbacks).
- Create a flawless and transparent execution trace viewer.
- Maintain decoupled independence from the Python engine internals.

## 4. Stakeholders
- **Project Lead**: Defines architecture and ensures SIH problem statement compliance.
- **Frontend Developer**: The primary consumer of this SRS.
- **Hackathon Judges**: The end-evaluators who will scrutinize the UX, honesty, and UI responsiveness.

---

## 5. User Personas

### 1. Remote-Sensing Expert
- **Goals**: Extract SAR backscatter data and multi-temporal statistics.
- **Technical Knowledge**: High (understands CRS, radiometric calibration, VQA).
- **Pain Points**: Dumbed-down "AI magic" that hides the actual process.
- **UI Requirements**: Needs raw trace arrays, bounding box exactness, metadata visibility.

### 2. Government Analyst
- **Goals**: Monitor illicit border activities or infrastructure growth.
- **Technical Knowledge**: Medium.
- **Pain Points**: Complicated GIS suites like QGIS are too slow for fast intelligence queries.
- **UI Requirements**: Wants an explicit text answer combined with a high-contrast bounding box.

### 3. Disaster-Management Analyst
- **Goals**: Identify flooded zones immediately.
- **Technical Knowledge**: Low-to-Medium.
- **Pain Points**: Time-wasting configuration.
- **UI Requirements**: Upload -> Query -> Highlight. Speed is paramount.

### 4. Agricultural Analyst
- **Goals**: Monitor crop health using multispectral/optical.
- **Technical Knowledge**: Medium.
- **UI Requirements**: Side-by-side comparison viewers for seasonal changes.

### 5. Infrastructure/Urban Planner
- **Goals**: Analyze urban sprawl.
- **Technical Knowledge**: Medium.
- **UI Requirements**: Needs cross-modal (Optical + SAR) to detect structures through clouds.

### 6. Non-Expert User (Judge/Evaluator)
- **Goals**: Evaluate the hackathon submission.
- **Technical Knowledge**: Varies wildly.
- **Pain Points**: Confusing UI, broken flows, fabricated data.
- **UI Requirements**: Immediate clarity, scientific honesty indicators, visible fallback traces.

---

## 6. UX Principles

1. **Scientific Honesty**: The UI must never hallucinate certainty. If a result is a fallback, display it loudly. If confidence is `null`, display `Confidence Unavailable`.
2. **Evidence-First Results**: Answers mean nothing without spatial/visual proof. The UI must prioritize rendering Bounding Boxes and Change Masks.
3. **Transparency**: The backend Execution Trace must be accessible, showing exact models and tools used to derive the answer.
4. **Progressive Disclosure**: Keep the main UI clean. Hide complex metadata, raw JSON traces, and raster bands behind tooltips and expandable drawers.
5. **Simplicity**: No complex GIS layer trees.
6. **Accessibility & Responsive**: Must work flawlessly on standard 1080p desktop monitors (SIH presentation format). Graceful degradation to tablet.

---

## 7. Information Architecture

### Main Routes
- **`/` (Dashboard / Analyzer)**: The primary single-page experience. Contains upload, query, and visualization panels.
- **`/history`**: A list of past queries/jobs stored in local storage (or via backend if a database is added later).
- **`/help` (or Modal)**: Instructions on query capabilities and accepted image formats.

*Note: For a hackathon, a single-page analyzer (`/`) is heavily preferred over multi-page routing to maintain context.*

---

## 8. Technology Decision

**Selected Stack**: **React 18 + Vite + TypeScript + Tailwind CSS**
- **Why React/Vite?**: Next.js App Router introduces unnecessary SSR/Node.js overhead for a tool that primarily uploads large local files and polls a separate Python FastAPI backend. Vite offers sub-second HMR on low-spec laptops.
- **Why TypeScript?**: Essential for mapping the complex `EngineResult` and `EvidenceBundle` dataclasses. Prevents massive runtime errors.
- **Why Tailwind CSS?**: Rapid prototyping without massive CSS files. Easy to build scientific aesthetics.
- **Mapping Library**: **Leaflet (react-leaflet)** or **OpenLayers**. Leaflet is highly recommended for hackathon speed when dealing with simple bounding boxes over static images.

---

## 9. UI Design System

- **Color System**:
  - Background: Dark Mode by default `#121212` (scientific/terminal feel) or high-contrast Light mode `#f8fafc`. Let's mandate a clean, crisp Light mode for government aesthetic, with slate/indigo accents.
  - Primary: `#4338ca` (Indigo 700)
  - Success/Water: `#0369a1` (Sky 700)
  - Change/Alert: `#b91c1c` (Red 700)
  - Warning/Fallback: `#d97706` (Amber 600)
- **Typography**: Inter or Roboto (clean, readable). Monospace (Fira Code) for Execution Traces.
- **Cards**: Flat with subtle borders (`border-slate-200`), no heavy shadows.
- **Buttons**: Sharp corners (rounded-sm), high contrast.
- **Badges**: Pill-shaped for `TaskType` and `Modality` tags.
- **Loading States**: Skeleton loaders for images, pulsing text for backend polling.

---

## 10. Main Application Layout

**Desktop Priority (1080p)**:
```text
+---------------------------------------------------------+
| [LOGO] SatQuery AI                        [New Query]   |
+----------------------+----------------------------------+
| 1. UPLOAD PANEL      | 3. VIEWER PANEL (Main Map/Image) |
| [ Dropzone ]         |                                  |
| [ Metadata ]         |                                  |
+----------------------+                                  |
| 2. QUERY PANEL       |                                  |
| [ Text Input ]       |                                  |
| [ Submit ]           |                                  |
+----------------------+----------------------------------+
| 4. EXECUTION TRACE   | 5. EVIDENCE & RESULTS            |
| (Expandable drawer)  | [ Answer ] [ Confidence ]        |
+----------------------+----------------------------------+
```
On Mobile: Stack 1, 2, 3, 5, 4.

---

## 11. Image Upload Experience

- **Single Image**: User drops one `.tif`. UI detects format and requests basic metadata from backend or frontend parser.
- **Temporal Pair**: User drops two images. UI must allow user to designate `BEFORE` and `AFTER` (or auto-sort by filename/metadata if available).
- **Cross-Modal Pair**: User drops Optical and SAR. UI must allow user to tag which is `OPTICAL` and which is `SAR`.
- **Validation**: Frontend checks extension (`.tif`, `.tiff`). Frontend MUST NOT block execution based on advanced CRS checks; backend is authoritative.

---

## 12. GeoTIFF Metadata UI

When an image is loaded, a small expandable card should display:
- **Dimensions**: `width` x `height`
- **Modality**: `Optical` | `SAR`
- **Role**: `Before` | `After` (if temporal)
*(Frontend will populate this via `ImageAsset` metadata returned from the backend after upload).*

---

## 13. Query Interface

- **Input**: `textarea` with auto-resize.
- **Suggested Queries**: Clickable pills below the input that auto-fill the textarea based on uploaded images.
  - If 1 image: "Find the river", "Describe this scene"
  - If 2 temporal: "What changed?"
  - If Optical+SAR: "Classify using SAR and optical"
- **Submit**: Blocked if 0 images uploaded. Changes to a `Cancel` button during polling.

---

## 14. Workflow Visualization

Once the backend Planner generates a `WorkflowPlan` (visible via polling or trace), the UI should render a small horizontal pipeline:
`Planner -> [Tool Name] -> Validator -> Complete`
This helps judges understand the agentic flow.

---

## 15. Processing State

- **Uploading**: "Uploading assets to engine..."
- **Running**: "Engine analyzing query..."
- **Polling**: Use deterministic intervals (e.g., 2000ms). Do NOT show fake percentages. Use an indeterminate spinner.

---

## 16. Result Experience

The Results Panel must clearly separate:
1. **The Answer**: Large text block. (e.g., "Based on spatial evidence, there are 1 distinct changed regions...")
2. **Confidence**: A specific badge. If `null`, show a gray badge: `Confidence: N/A (Deterministic)`.
3. **Fallback Warning**: If `fallback_triggered: True` in evidence metadata, show a bright Amber alert box:
   `⚠️ Advanced multimodal model unavailable. Result generated using deterministic cross-modal analysis fallback.`

---

## 17. Visual Evidence

Evidence data comes from `EvidenceBundle`.
- **Bounding Boxes**: Mapped over the image viewer. Render `BoundingBox.label` on hover.
- **Change Masks**: If `change_mask` is returned (e.g., path to overlay image or raw pixels), overlay it on the viewer with 50% opacity in Red.
- **Textual Evidence**: Displayed as bullet points under the main answer.

---

## 18. Image Viewer

- Use **React-Leaflet** with `L.imageOverlay` for rendering GeoTIFFs (converted to PNGs by the backend for web display, or use a frontend GeoTIFF layer if preferred, but backend PNG generation is safer for hackathons).
- Must support panning and zooming.
- Must have a layer control toggle to turn Bounding Boxes and Masks on/off.

---

## 19. Temporal Comparison UI

If the task is `TEMPORAL_CHANGE_DETECTION` or `VQA`:
- Implement a **Split-Screen** or **Slider** (Swipe) viewer.
- Left side: BEFORE image. Right side: AFTER image.
- Change masks should overlay on BOTH sides simultaneously.

---

## 20. Cross-Modal UI

If `CROSS_MODAL_OPTICAL_SAR`:
- Standard layer toggle allowing the user to switch the base map between Optical and SAR.
- Evidence (e.g., water agreement bounding boxes) overlays on top, independent of the active base map layer.

---

## 21. Fallback UI

Trigger: `EvidenceBundle.metadata.fallback_triggered === True`.
UI Element:
```html
<div class="bg-amber-50 border-l-4 border-amber-500 p-4">
  <p class="font-bold text-amber-800">System Fallback Activated</p>
  <p>{EvidenceBundle.metadata.fallback_reason}</p>
</div>
```

---

## 22. Execution Trace UI

The `EngineResult.execution_trace` is a `List[Dict[str, Any]]`.
Create an accordion/drawer labeled "Execution Trace (Agentic Flow)".
Map through the list and render each step as a JSON tree or a simplified timeline.
```json
// Example trace step rendered beautifully
{
  "tool": "croma_specialist",
  "duration_ms": 120,
  "result_summary": "Fallback initiated..."
}
```

---

## 23. Confidence UI

Trigger: `EngineResult.confidence`.
If `null`: Render as a muted badge "Confidence: Not Applicable (Deterministic/Heuristic)".
If `float` (e.g., `0.92`): Render as "Confidence: 92%" with a green badge if > 80%, yellow if > 50%, red if < 50%.

---

## 24. Error Experience

If `EngineResult.status === 'failed'` or HTTP 500:
- Show a Red Alert box.
- Iterate over `EngineResult.errors` (`List[EngineError]`).
- Display `error.code` and `error.message`.
- Provide a "Retry Query" button.

---

## 25. API Contract

The frontend assumes a standard asynchronous polling REST API provided by FastAPI (Phase 2):

1. **Upload**: `POST /api/v1/assets` -> Returns `ImageAsset` objects.
2. **Submit Job**: `POST /api/v1/jobs`
   Body: `{ query: "...", images: ["id1", "id2"] }`
   Returns: `{ job_id: "uuid" }`
3. **Poll Job**: `GET /api/v1/jobs/{job_id}`
   Returns: `{ status: "running" | "success" | "failed", result: EngineResult | null }`

*Note: Since the backend is unwritten, the frontend developer should abstract API calls into a service layer so they can be easily swapped.*

---

## 26. Frontend Data Types

```typescript
// types/engine.ts

export enum TaskType {
    SINGLE_IMAGE_VQA = "single_image_vqa",
    SINGLE_IMAGE_CAPTION = "single_image_caption",
    SINGLE_IMAGE_GROUNDING = "single_image_grounding",
    TEMPORAL_CHANGE_DETECTION = "temporal_change_detection",
    TEMPORAL_CHANGE_DESCRIPTION = "temporal_change_description",
    TEMPORAL_CHANGE_VQA = "temporal_change_vqa",
    CROSS_MODAL_OPTICAL_SAR = "cross_modal_optical_sar",
    CROMA_CLASSIFICATION = "croma_classification"
}

export interface BoundingBox {
    label: string;
    coordinates: number[];
    confidence?: number;
    source: string;
}

export interface ChangeMask {
    width: number;
    height: number;
    mask_path?: string;
    threshold_used?: number;
    changed_pixel_count: number;
    changed_fraction: number;
}

export interface EvidenceBundle {
    textual_evidence?: string;
    bounding_boxes: BoundingBox[];
    visualizations: string[];
    change_statistics?: Record<string, any>;
    change_mask?: ChangeMask;
    metadata: Record<string, any>;
}

export interface EngineError {
    code: string;
    message: string;
}

export interface SpecialistResult {
    status: string;
    model_name: string;
    task: TaskType;
    answer: any;
    confidence?: number;
    evidence: EvidenceBundle;
    metadata: Record<string, any>;
    execution_time: number;
    error?: string;
}

export interface EngineResult {
    request_id: string;
    status: string;
    query: string;
    task?: TaskType;
    answer: any;
    confidence?: number;
    specialist_results: SpecialistResult[];
    evidence: EvidenceBundle[];
    execution_trace: Record<string, any>[];
    errors: EngineError[];
}
```

---

## 27. State Management

- Use **React `useState`** and **`useReducer`** for localized form state (uploading images, holding query string).
- Use **Zustand** (or React Context) for the global `JobState` (idle -> uploading -> polling -> success/error) so the Viewer and Results panels can subscribe to the same `EngineResult` object without prop drilling.

---

## 28. File and Component Architecture

```text
src/
├── api/
│   ├── client.ts        // Axios instance
│   └── jobs.ts          // Job polling logic
├── components/
│   ├── ui/              // Reusable Tailwind components (Buttons, Cards, Badges)
│   ├── upload/          // Dropzone, Asset list
│   ├── viewer/          // React-Leaflet wrapper, Overlays, Temporal Slider
│   ├── query/           // Textarea, Suggestion pills
│   ├── results/         // Answer box, Confidence Badge, Fallback Alert
│   └── trace/           // Execution trace accordion
├── store/
│   └── useAppStore.ts   // Zustand store
├── types/
│   └── engine.ts        // TypeScript interfaces
├── App.tsx              // Main layout grid
└── main.tsx
```

---

## 29. Accessibility

- All images must have `alt` text.
- Dropzones must be keyboard navigable (`tabIndex={0}`, `onKeyDown`).
- Fallback alerts must use `role="alert"` for screen readers.
- Colors must meet WCAG AA contrast (e.g., white text on indigo-700 background).

---

## 30. Performance

- Do NOT decode `.tif` files in the browser using heavy WASM libraries unless strictly required. The API contract assumes the backend converts `.tif` to web-friendly overlays (PNG/JPG) and returns them in `visualizations`.
- Unmount the Leaflet viewer completely when switching between wildly different tasks to prevent WebGL context leaks.
- Ensure the polling interval clears cleanly on unmount (`clearInterval`).

---

## 31. Security

- Escape all `textual_evidence` and `answer` fields before rendering. Do not use `dangerouslySetInnerHTML`.
- No API keys are required in the frontend; it relies on the local FastAPI instance.

---

## 32. Testing

**Testing Stack**: Vitest + React Testing Library.
Required tests:
1. `UploadZone.test.tsx`: Prevents non-image uploads.
2. `ResultsPanel.test.tsx`: Renders Fallback UI when `fallback_triggered` is true.
3. `ResultsPanel.test.tsx`: Hides confidence when `null`.
4. `useAppStore.test.ts`: State transitions from `idle` -> `polling` -> `success`.
5. `TraceAccordion.test.tsx`: Maps arrays into valid lists.

---

## 33. Mock Development Mode

Create a file `src/api/mockData.ts` containing a hardcoded `EngineResult` representing a successful `CROSS_MODAL_OPTICAL_SAR` fallback (matching Engine V1 E11 test).
If `VITE_USE_MOCK=true`, the `jobs.ts` service instantly returns this mock data instead of calling the backend.

---

## 34. Environment

`.env` configuration:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```
Build commands:
```bash
npm run dev
npm run build
npm run preview
```

---

## 35. Deployment

- Build output (`dist/`) will be generated via `npm run build`.
- For the SIH hackathon, the frontend will likely be served statically by the FastAPI backend (Phase 2), or run concurrently via a script.
- Ensure all API routes are relative (e.g., `/api/v1`) or configurable via environment variables to avoid CORS issues in production.

---

## 36. Demo Mode

During the hackathon pitch, network connectivity or heavy GPU tasks may fail.
The UI must have a hidden keystroke (e.g., `Ctrl+Shift+D`) that injects pre-computed `EngineResult` payloads to guarantee a flawless 3-minute presentation.

---

## 37. Acceptance Criteria

| ID | Description | Component |
|---|---|---|
| FE-01 | App loads without console errors | App.tsx |
| FE-02 | Dropzone accepts up to 2 images | UploadZone |
| FE-03 | Query blocks submission if no images | QueryPanel |
| FE-04 | Job state changes to "Polling..." | AppStore |
| FE-05 | Renders text answer correctly | ResultsPanel |
| FE-06 | Displays "Fallback Activated" warning if triggered | ResultsPanel |
| FE-07 | Displays Bounding Boxes on Leaflet map | Viewer |
| FE-08 | Displays Execution Trace JSON nicely | TracePanel |

---

## 38. Developer Implementation Order

1. **Bootstrap**: Init Vite + React + TS. Install Tailwind.
2. **Types**: Copy `types/engine.ts`.
3. **Mock Data**: Create `mockData.ts` to unblock UI dev.
4. **Layout**: Build the grid layout.
5. **Upload & Query**: Wire up forms to Zustand store.
6. **Results Panel**: Build answer, confidence, trace, fallback UI.
7. **Viewer**: Integrate React-Leaflet and overlay dummy PNGs.
8. **API Client**: Swap mock for real Axios calls.

---

## 39. Git Rules

- Branch: `feat/frontend`
- Commit format: `feat(ui): add Leaflet viewer component`
- DO NOT touch `engine/` or `tests/` directories.

---

## 40. Merge Contract

The frontend assumes the FastAPI backend (yet to be built) will perfectly wrap the `SatQueryEngine.analyze()` method and return the exact JSON serialization of the dataclasses defined in `engine.contracts`.

---

## 41. Glossary
- **SRS**: Software Requirements Specification
- **SIH**: Smart India Hackathon
- **VQA**: Visual Question Answering
- **SAR**: Synthetic Aperture Radar
- **Engine V1**: The frozen python backend computation core.
