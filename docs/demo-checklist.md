# SATQUERY AI — DEMO CHECKLIST

## Prerequisites
1. **Start Backend**: Run the FastAPI server locally from the project root.
   \\\ash
   $env:PYTHONPATH="."; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
   \\\
2. **Start Frontend**: Run the React frontend locally.
   \\\ash
   npm run dev
   \\\
3. **GeoChat Worker**: Ensure the Lightning T4 worker is active if running real VQA inference, and set \VITE_USE_MOCK=false\ in your \.env\.

## 1. Single-Image VQA Demo
- [ ] Upload a single optical image.
- [ ] Select the "Single Image" workflow.
- [ ] Type a question: "What are the major land-cover features visible in this image?"
- [ ] Verify the system responds with a textual answer.

## 2. Spatial Grounding Demo
- [ ] Upload an optical image.
- [ ] Select the "Grounding" workflow.
- [ ] Type a question: "Where are the buildings?"
- [ ] Verify the bounding boxes are successfully rendered on the image overlay.

## 3. Temporal Change Demo
- [ ] Upload two optical images (set roles to "Before" and "After").
- [ ] Select the "Temporal Change" workflow.
- [ ] Type a request: "Detect changes between these images."
- [ ] Verify the UI displays physical/statistical results (e.g., "CHANGED FRACTION") and the change mask overlay.

## 4. Optical + SAR Demo
- [ ] Upload an optical image and a SAR image.
- [ ] Manually explicitly set the Modality in the UI to "Optical" and "SAR" for each respective image.
- [ ] Select the "Optical + SAR" workflow.
- [ ] Type a request: "Fuse optical and SAR data."
- [ ] Verify cross-modal bounding boxes and statistical metadata are shown.

## Verifying Integrity
- [ ] **Evidence**: Confirm that specific visual masks, coordinates, and deterministic output strings are displayed in the Evidence panel.
- [ ] **Trace**: Confirm the Execution Trace displays the deterministic orchestrator steps without hallucinated tasks.
- [ ] **Confidence**: Confirm the confidence badge prominently displays "NOT CALIBRATED" when executing fallback or non-calibrated paths.
- [ ] **Error Handling**: Upload an unsupported file (e.g., \.txt\) and confirm the frontend gracefully handles the backend 400 Bad Request error without crashing.
