# SATQUERY AI — DEMO RUNBOOK

This runbook outlines the required environment, startup commands, and reliable demo pathways for SatQuery AI.

## A. Laptop Prerequisites
- **OS**: Windows / Linux / macOS
- **RAM**: Minimum 8GB (Mock Mode), 16GB (Real Mode recommended)
- **Disk**: 1GB free for repositories and baseline models.

## B. Python Environment
- **Python Version**: 3.10 or 3.12+
- **Packages**: fastapi, uvicorn, rasterio, numpy
- **Install**: pip install -r requirements/base.txt

## C. Node Environment
- **Node Version**: v18+
- **Packages**: Run npm install
- **Build**: Run npm run build

## D. Backend Startup Command
Start the FastAPI backend locally in the project root:
\\\ash
$env:PYTHONPATH="."; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
\\\

## E. Frontend Startup Command
Start the React application locally in the project root:
\\\ash
npm run dev
\\\

## F. Optional GeoChat Worker Configuration
If deploying the real VLM on a Lightning T4 GPU instance:
1. Ensure the worker node is online.
2. The engine's remote requests.post() inside remote_sensing_vqa.py will automatically bridge the connection if configured in the .env.

## G. Required Environment Variables
Create a .env file in the root if not present (copy .env.example).
To test Real AI, ensure:
\\\
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://127.0.0.1:8000
SATQUERY_MODEL_MODE=real
\\\
*(For the Zero-Budget / Offline Mock demo, use VITE_USE_MOCK=true and SATQUERY_MODEL_MODE=mock)*.

## H. Four Demo Scenarios

### 1. Single Image VQA
- **Input**: Any optical GeoTIFF.
- **Action**: Select the 'Single Image' mode.
- **Request**: "What are the major land-cover features visible in this image?"
- **Behavior**: System streams a textual analysis of the landscape.

### 2. Spatial Grounding
- **Input**: Any optical GeoTIFF.
- **Action**: Select the 'Grounding' mode.
- **Request**: "Highlight the buildings." *(Note: the deterministic planner strictly looks for the 'highlight' or 'ground' keywords to explicitly route to the bounding-box pathway).*
- **Behavior**: System draws SVG-scalable bounding boxes over the requested regions.

### 3. Temporal Change
- **Input**: Two optical GeoTIFFs (Before and After).
- **Action**: Select the 'Temporal Change' mode.
- **Request**: "Detect changes between these images."
- **Behavior**: System computes pixel-level changes and renders the change mask along with physical change fractions.

### 4. Optical + SAR
- **Input**: One Optical GeoTIFF and one SAR GeoTIFF.
- **Action**: Use the Modality Badges on the upload cards to explicitly label one "Optical" and one "SAR".
- **Request**: "Analyze the optical and SAR observations together."
- **Behavior**: The pretrained CROMA backbone pathways correlate cross-modal structural cues.

## I. Fallback Procedure (Zero-Budget Demo)
If the remote GPU is unavailable, internet goes down, or the live GeoChat API drops:
1. The engine automatically routes to mock adapters.
2. The UI will instantly display deterministic physical bounds and vocabulary responses.
3. The demo proceeds smoothly without a fatal crash, highlighting the defensively programmed orchestration tier.

## J. Common Failure Recovery
- **Error**: Unsupported file type. -> Ensure the user uploaded a .tif, .png, or .jpg.
- **Error**: Maximum of 2 images supported. -> Remove extra files from the dropzone.
- **No Bounding Boxes**: The SVG engine requires non-zero areas; ensure the model output generated valid geometries.

## K. Demo-Day Checklist
- [ ] Backend running? (http://127.0.0.1:8000/health)
- [ ] Frontend running? (http://localhost:5173)
- [ ] Sample TIFF files accessible on the presentation machine?
- [ ] VITE_USE_MOCK set according to network availability?
