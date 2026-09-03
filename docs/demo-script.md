# SATQUERY AI — JUDGE DEMO SCRIPT

*This script outlines the exact narrative flow to demonstrate SatQuery AI to an evaluator. It highlights the functional capabilities without over-promising AI semantics.*

---

### SCENE 1: The Context & VQA (Single Image Analysis)
**Speaker**: "Imagine an analyst receives a fresh optical satellite image from a recent acquisition."
*? Action: Upload a single optical GeoTIFF.*
*? Action: Select 'Single Image' mode.*
**Speaker**: "Instead of manually inspecting every region for general context, they can query the platform directly using natural language."
*? Action: Type: 'What are the major land-cover features visible in this image?'*
**Speaker**: "The orchestrator receives this query and routes it to the VQA module. The system returns a descriptive summary. Note that the trace correctly displays this execution path, and our Confidence Badge actively warns the user when the model is not statistically calibrated, enforcing scientific honesty."

### SCENE 2: Grounding (Spatial Verification)
**Speaker**: "Now, I need to know *where* these relevant objects are."
*? Action: Select 'Grounding' mode.*
*? Action: Type: 'Highlight the buildings.'*
**Speaker**: "The planner interprets the explicit request for spatial grounding. It invokes the grounding specialist to extract coordinates. We seamlessly map these generated geometries onto our scalable UI, allowing analysts to instantly locate points of interest without manual annotation."

### SCENE 3: Temporal Change (Before & After)
**Speaker**: "Suppose we receive another observation of the exact same area following an event."
*? Action: Upload two optical images (Before and After).*
*? Action: Select 'Temporal Change' mode.*
*? Action: Type: 'Detect changes between these images.'*
**Speaker**: "The system securely aligns the rasters and triggers our deterministic change detector. Rather than hallucinating semantic labels—like falsely claiming a building was demolished—our engine produces a rigorous, pixel-level statistical difference. We render the change fraction and a visual mask for physical verification."

### SCENE 4: Cross-Modal Fusion (Optical + SAR)
**Speaker**: "Finally, optical imagery may not tell the whole story, especially under cloud cover."
*? Action: Upload one Optical and one SAR GeoTIFF. Explicitly assign the Modalities via the UI dropdowns.*
*? Action: Select 'Optical + SAR' mode.*
*? Action: Type: 'Analyze the optical and SAR observations together.'*
**Speaker**: "Using a pretrained CROMA backbone for robust feature extraction, our system evaluates both observations. It outputs regions of physical and statistical agreement where both radar backscatter and optical reflectance align. It does not blindly classify semantics; it acts as a deterministic, mathematically grounded analytical partner."

### SCENE 5: Resilience & Safety (Zero-Budget Mock)
**Speaker**: "And importantly, SatQuery AI is defensively programmed for deployment in edge environments. If our cloud GPU drops offline, the system safely falls back to deterministic mocked responses. It gracefully handles malformed data—like an unsupported text file—by throwing clean validation errors without leaking internal stack traces or crashing the application."
*? Action: Upload an invalid .txt file to show the safe error banner.*
