# SatQuery AI — Remote Sensing & AI Learning Guide

> A continuously updated knowledge reference for the concepts, sensors, datasets, models, and terminology used by SatQuery AI.

## Living Document Rule

Whenever a future SatQuery development day introduces a new:
- remote-sensing concept
- sensor
- dataset
- model
- architecture
- preprocessing method
- evaluation metric
- geospatial concept
- AI technique
- acronym
- domain-specific term

**UPDATE THIS FILE.**

Do not create a new learning document for every term unless the subject is large enough to justify its own document. This document records: *"WHAT THE TERMS AND TECHNOLOGIES MEAN."*

---

## Table of Contents
1. [Remote Sensing Basics](#1-remote-sensing-basics)
2. [Satellite Sensors](#2-satellite-sensors)
3. [Optical / Multispectral Imagery](#3-optical--multispectral-imagery)
4. [SAR Imagery](#4-sar-imagery)
5. [Optical vs SAR](#5-optical-vs-sar)
6. [Temporal Imagery](#6-temporal-imagery)
7. [Temporal Change Detection](#7-temporal-change-detection)
8. [Cross-Modal Remote Sensing](#8-cross-modal-remote-sensing)
9. [Georeferencing](#9-georeferencing)
10. [Co-Registration](#10-co-registration)
11. [GeoTIFF](#11-geotiff)
12. [Remote-Sensing AI](#12-remote-sensing-ai)
13. [Vision-Language Models (VLMs)](#13-vision-language-models-vlms)
14. [CROMA](#14-croma)
15. [CROMA Inputs](#15-croma-inputs)
16. [CROMA Downstream Task](#16-croma-downstream-task)
17. [Remote-Sensing Datasets](#17-remote-sensing-datasets)
18. [Preprocessing](#18-preprocessing)
19. [Tiling](#19-tiling)
20. [Evidence-Grounded AI](#20-evidence-grounded-ai)
21. [Confidence](#21-confidence)
22. [Agentic Orchestration](#22-agentic-orchestration)
23. [SatQuery Task Taxonomy](#23-satquery-task-taxonomy)
24. [Common Mistakes](#24-common-mistakes)
25. [SatQuery Glossary](#25-satquery-glossary)
26. ["If You Only Remember 10 Things"](#26-if-you-only-remember-10-things)
27. [Learning Resources](#27-learning-resources)
28. [Project-Specific vs General Knowledge](#28-project-specific-vs-general-knowledge)
29. [Update History](#29-update-history)
30. [Future Update Rule](#30-future-update-rule)

---

## 1. Remote Sensing Basics

### What is Remote Sensing?
Remote sensing is the process of detecting and monitoring the physical characteristics of an area by measuring its reflected and emitted radiation at a distance (typically from satellite or aircraft). 

The basic flow is:
```text
satellite/sensor
       ↓
electromagnetic energy / radar signal
       ↓
measurement
       ↓
image
       ↓
information extraction
```

**Distinctions:**
- **Satellite imagery**: Captured from space (e.g., Copernicus Sentinel, Landsat).
- **Aerial imagery**: Captured from planes/drones (usually higher resolution but less global coverage).
- **Remote sensing**: The science of obtaining information about objects/areas from a distance.
- **GIS (Geographic Information Systems)**: The software/framework used to store, analyze, and visualize geographic data.

---

## 2. Satellite Sensors

Different sensors observe entirely different physical properties of the Earth.

| Sensor type | Measures | Typical information | Day/night | Cloud sensitivity |
|---|---|---|---|---|
| **Optical** | reflected radiation | color/spectral properties | mostly daytime | affected by clouds |
| **Multispectral** | multiple spectral bands | vegetation/water/land cover | daytime | affected by clouds |
| **SAR** | radar backscatter | structure/roughness/moisture | day/night | works through clouds |

**Why SatQuery cares**: We cannot treat all satellite images as ordinary RGB photographs. A SAR image requires entirely different mathematical and neural network treatment than an optical image.

---

## 3. Optical / Multispectral Imagery

- **Pixel**: The smallest unit of a digital image.
- **Band**: A specific slice of the electromagnetic spectrum (e.g., Red, Near-Infrared).
- **Multispectral**: Imagery capturing data at specific frequencies across the electromagnetic spectrum.
- **Hyperspectral**: Imagery capturing data across hundreds of contiguous narrow bands.
- **Sentinel-2**: An optical Earth observation mission providing high-resolution multispectral imagery (up to 13 bands).
- **Reflectance**: The proportion of light/radiation hitting a surface that is reflected back to the sensor.
- **Radiance**: The total amount of light energy arriving at the sensor.
- **Resolution**: Typically *spatial resolution*—the physical size of a pixel on the ground (e.g., 10m/pixel).

**Why Sentinel-2 12-band input is different from RGB visualization:**
While you can map specific bands to create a visual picture for humans:
```text
RGB visualization:

B4 → Red
B3 → Green
B2 → Blue
```
...a multimodal model like CROMA actively uses the invisible bands (like Near-Infrared or Shortwave Infrared) to detect patterns invisible to the naked eye, such as vegetation health or moisture.

---

## 4. SAR Imagery

### What is SAR?
SAR stands for **Synthetic Aperture Radar**. It is an *active* sensor, meaning the satellite generates its own energy (microwave pulses) and measures what bounces back (backscatter), rather than relying on the Sun.

- **Active sensor**: Provides its own illumination.
- **Microwave**: Long wavelengths that pass through clouds and weather.
- **Backscatter**: The portion of the radar signal redirected back to the antenna.
- **Amplitude / Power**: Measurements of the signal strength.
- **dB (Decibels)**: A logarithmic scale commonly used to express SAR backscatter.
- **Speckle**: A granular, grainy noise inherent to radar imagery caused by signal interference.
- **VV / VH**: Polarization states. V = Vertical. VV means the radar sent a vertical wave and measured the vertical return. VH means vertical sent, horizontal received.

**Why SAR is useful:**
SAR can image the Earth through thick clouds, smoke, and total darkness. It strongly reveals structural geometry (like buildings or ships) and surface roughness/moisture.

**Limitations:**
SAR does not "see everything." It cannot see colors, it suffers from radar shadows in mountainous or urban areas, and interpreting its imagery is counterintuitive to the human eye.

---

## 5. Optical vs SAR

| Property      | Optical                    | SAR                                      |
| ------------- | -------------------------- | ---------------------------------------- |
| **Energy source** | Sun / reflected radiation  | Sensor emits radar                       |
| **Day/night**     | mostly daytime             | yes                                      |
| **Clouds**        | affected                   | largely unaffected                       |
| **Appearance**    | intuitive visual           | radar backscatter                        |
| **Structure**     | indirect                   | often strong structural response         |
| **Vegetation**    | spectral information       | structural/moisture information          |
| **Water**         | often dark/low reflectance | often low backscatter, context dependent |

### Why combine them?
Optical and SAR provide *complementary* information.

```text
Optical:
"What does the surface look like spectrally?"

SAR:
"How does the surface interact with radar?"

Together:
"Can we obtain a more complete description?"
```
For example, built-up areas might look like bare soil in optical imagery, but SAR clearly shows the double-bounce radar reflection of buildings. Combining them prevents false classifications.

---

## 6. Temporal Imagery

### What is a Bi-Temporal Image Pair?
Two images covering the same (or very similar) geographic area acquired at **different times**.

```text
T1 ── Before
T2 ── After
```

- **Temporal pair**: Images linked by a time difference.
- **Change detection**: Identifying pixels/regions that altered.
- **Change description**: Generating text explaining *what* changed.
- **Change VQA**: Answering questions about the change.

**Crucial Distinction:**
```text
Before + After ≠ Optical + SAR
```
- **Temporal**: Same modality, different time.
- **Cross-modal**: Different modalities, same time.

---

## 7. Temporal Change Detection

The basic workflow:
```text
Image T1
   +
Image T2
   ↓
registration
   ↓
comparison
   ↓
change map
   ↓
changed regions
```

**Why registration is essential:** If the images are slightly misaligned, the system will hallucinate changes simply because the pixels shifted.

**Semantic understanding vs Pixel differences:**
A simple subtraction can tell you pixels changed. It takes AI to say:
*Building absent in T1 + Building present in T2 → "New construction detected."*
SatQuery cares about semantic meaning, not just mathematical differences.

---

## 8. Cross-Modal Remote Sensing

```text
Optical
   +
SAR
   ↓
cross-modal reasoning
```

**Cross-modal** means reasoning across different sensor types.
- **Modality**: The type of data (e.g., Optical, SAR, Text).
- **Fusion**: Combining data from multiple modalities.
- **Early fusion**: Stacking the image bands together before feeding them into a model.
- **Late fusion**: Processing images independently, then combining their high-level predictions.
- **Feature fusion / Cross-attention**: Allowing the neural networks to exchange information at intermediate layers (e.g., CROMA).
- **Joint representation**: A single mathematical embedding that encapsulates information from both modalities.

---

## 9. Georeferencing

- **CRS (Coordinate Reference System)**: Defines how 2D map coordinates relate to real places on Earth.
- **EPSG**: A registry of standard CRS codes (e.g., EPSG:4326 is standard GPS lat/lon).
- **Bounding box (bbox)**: The min/max coordinates outlining an image's spatial extent.
- **Affine transform**: A matrix that translates raw pixel row/col indices into real-world geographic coordinates.
- **Spatial resolution**: Meters per pixel.

**Example:**
```text
Pixel coordinate: (x=200, y=100)
Geospatial coordinate: (latitude 45.0, longitude -120.0)
```
**Why SatQuery cares**: Without georeferencing, bounding boxes from an AI model are just raw pixels. To plot them on a real map, the engine must convert pixel bounds to geospatial coordinates.

---

## 10. Co-Registration

**What does "co-registered" mean?**
Two images are spatially aligned so corresponding pixels refer to the exact same ground area.

```text
Optical pixel (100,100)
        ↕
SAR pixel (100,100)
```
**Why it matters**: Blindly subtracting or feeding unaligned images into a multimodal network is scientifically invalid. They must be registered/warped to the same grid first.

---

## 11. GeoTIFF

**What is a GeoTIFF?**
An image format (TIFF) with embedded geographic metadata.

Metadata includes:
- **width / height**: Image dimensions.
- **band count**: Number of channels.
- **dtype**: Data type (e.g., uint8, float32).
- **CRS**: The projection system.
- **transform**: How to map pixels to Earth.
- **nodata**: A special value indicating "no valid data here" (e.g., image edges).

**Why SatQuery reads metadata**: Loading massive 10GB satellite arrays directly into RAM crashes computers. SatQuery reads the lightweight metadata first to plan processing before extracting small, safe tiles.

---

## 12. Remote-Sensing AI Tasks

| Task             | Question it answers               |
| ---------------- | --------------------------------- |
| **Classification**   | What is in this image/patch?      |
| **Detection**        | Where are the objects?            |
| **Segmentation**     | Which pixels belong to what?      |
| **Captioning**       | What is visible?                  |
| **VQA**              | Answer a question about the image |
| **Grounding**        | Where is the thing mentioned?     |
| **Change detection** | What changed?                     |

---

## 13. Vision-Language Models (VLMs)

**VLM** = Vision-Language Model.

```text
Image
  +
Text
  ↓
Vision-language model
  ↓
textual answer
```

**Why generic VLMs fail on satellite imagery:** Standard VLMs (like GPT-4V or LLaVA) are trained on horizontal, ground-level RGB photos. They struggle with vertical, top-down perspectives, false-color multispectral data, and SAR backscatter.

- **Remote-Sensing VLM**: A VLM explicitly fine-tuned on satellite data.
- **SatQuery Example**: We use **GeoChat**, a specialized RS VLM capable of grounding (identifying bounding boxes) and visual question answering (VQA) on satellite images.

---

## 14. CROMA

### What is CROMA?
**C**ontrastive **R**emote Sensing Representations with Multispectral and **O**ptical **M**asked **A**utoencoders.

CROMA is a remote-sensing multimodal **representation model**, *not* a natural-language VQA assistant.

Conceptually:
```text
Sentinel-2 (12 optical bands)
      ↓
Optical Encoder
      ↓
Optical representation

Sentinel-1 (2 SAR channels)
      ↓
SAR Encoder
      ↓
SAR representation

Optical + SAR
      ↓
Joint Encoder
      ↓
Joint representation
```

- **Contrastive learning**: Training a model by making similar pairs (e.g., co-located Optical and SAR) have similar mathematical embeddings.
- **Joint representation**: A shared 768-dimensional space encoding both modalities.

**IMPORTANT:** CROMA does not answer questions natively. 
```text
CROMA = representation
SatQuery = agent + specialist models + reasoning + evidence
```
SatQuery uses CROMA to extract powerful mathematical features, which are then passed to a separate classifier (downstream task) to produce geospatial evidence.

---

## 15. CROMA Inputs

CROMA strictly expects:
```text
Sentinel-2: 12 channels
Sentinel-1: 2 channels (VV, VH)
```
This is drastically different from GeoChat, which expects a 3-channel RGB image.

> **WARNING**: Never assume that every remote-sensing model expects RGB. Supplying an RGB image to CROMA is scientifically invalid.

---

## 16. CROMA Downstream Task

```text
Optical + SAR
       ↓
CROMA
       ↓
joint embedding
       ↓
downstream task (classifier)
       ↓
prediction
```
- **Linear probe**: A simple, single-layer neural network trained on top of a frozen model.
- **Frozen backbone**: The CROMA weights are locked and do not update during training.
- **Classifier head**: The small network we actually train to map the 768-d embedding to a class (e.g., Water / Built-up).

---

## 17. Remote-Sensing Datasets

| Dataset | Modalities | Main task | Relevance to SatQuery |
| ------- | ---------- | --------- | --------------------- |
| **BigEarthNet** | Optical | Classification | Researched (Baseline) |
| **BigEarthNet-MM** | Optical + SAR | Multi-label Class. | **Used for CROMA Downstream Classification** |
| **SEN12MS** | Optical + SAR | Segmentation | Researched |
| **RSVQA** | Optical | VQA | Researched |
| **CDVQA** | Bi-Temporal Optical | Change VQA | Researched (Temporal references) |
| **SpaceNet** | Optical/SAR | Building Detection | Researched |

*(Note: "Researched" means investigated during development. "Used" means SatQuery actively relies on it for architecture or training).*

---

## 18. Preprocessing

### Optical preprocessing
- **Nodata handling**: Ignoring invalid edges.
- **Percentile normalization**: Scaling pixels by avoiding extreme outlier values.
- **Scaling**: Dividing Sentinel-2 reflectance by 10000 to map it to a standard `[0, 1]` domain.

### SAR preprocessing
- **dB conversion**: Converting amplitude/power to decibels (`10 * log10(x)`).
- **Clipping**: Bounding the extreme dynamic range of radar returns.

### Why preprocessing is modality-specific
One normalization strategy should not automatically be applied to both. Optical reflectance requires linear scaling; SAR requires logarithmic scaling (dB) due to high dynamic range and speckle.

---

## 19. TILING

Large GeoTIFFs (e.g., 10,000 x 10,000 pixels) cannot fit directly into AI models.

```text
Large GeoTIFF
      ↓
TileGenerator
      ↓
small windows (e.g., 120x120)
      ↓
model
      ↓
results
      ↓
spatial aggregation
```

- **Tile / Window**: A small, manageable chunk of the image.
- **Overlap**: Ensuring tiles slightly overlap so objects on edges aren't cut in half.
- **Stride**: How far the window moves for the next tile.

---

## 20. Evidence-Grounded AI

"Evidence-grounded" means SatQuery must prove *why* it gave an answer.

Example:
```text
Text answer ("Built-up area detected")
+
bounding box (x_min, y_min, x_max, y_max)
+
source modality (Optical + SAR)
+
model used (CROMA-base + LinearProbe)
+
confidence (0.91)
+
execution trace
```

This is infinitely more reliable for a geospatial analyst than returning only:
*"The image contains buildings."*

---

## 21. Confidence

- **Confidence score / Probability**: A number (0.0 to 1.0) indicating how strongly the model believes its prediction.
- **Calibrated confidence**: A score that genuinely reflects real-world likelihood (rare).
- **Heuristic confidence**: A rule-based estimation.

**Important Warning**: Do not equate a raw neural-network softmax probability with guaranteed real-world certainty.

---

## 22. Agentic Orchestration

In SatQuery, "Agentic" does NOT necessarily mean "an LLM thinking freely." 
It means **controlled task routing and tool/model orchestration**:

```text
User query
   ↓
Planner (LLM or Rule-based)
   ↓
understand task & validate inputs
   ↓
select specialist (e.g., CROMASpecialist)
   ↓
execute
   ↓
collect evidence
   ↓
return formatted result
```

---

## 23. SatQuery Task Taxonomy

| Task Enum | Input | Specialist |
| --------------------------- | ----------------- | ----------------------- |
| `SINGLE_IMAGE_VQA`            | 1 image           | GeoChat (or mock)                 |
| `SINGLE_IMAGE_GROUNDING`      | 1 image           | Grounding specialist    |
| `SINGLE_IMAGE_CAPTIONING`     | 1 image           | Caption specialist      |
| `TEMPORAL_CHANGE_DETECTION`   | 2 temporal images | Change detector         |
| `TEMPORAL_CHANGE_DESCRIPTION` | 2 temporal images | Change specialist       |
| `TEMPORAL_CHANGE_VQA`         | 2 temporal images | Change VQA              |
| `CROSS_MODAL_OPTICAL_SAR`     | optical + SAR     | OpticalSARSpecialist (fallback) / CROMA     |
| `CROMA_CLASSIFICATION`        | optical + SAR     | CROMA + Downstream Head |

---

## 24. Common Mistakes

### Mistake 1: Treating SAR as an RGB photograph
SAR measures structural backscatter, not color. It is highly directional and noisy (speckle).

### Mistake 2: Using B4/B3/B2 for a model requiring all bands
Feeding RGB channels to a model like CROMA that expects 12 bands will cause tensor shape crashes or garbage predictions.

### Mistake 3: Comparing two unregistered images
Subtracting `T2 - T1` when pixels don't align spatially creates massive false-change errors.

### Mistake 4: Calling a random/untrained neural network an "AI model"
SatQuery explicitly requires real weights or transparently labeled baselines.

### Mistake 5: Calling a CROMA embedding a natural-language answer
CROMA outputs a math vector (`joint_GAP`), not English.

### Mistake 6: Claiming benchmark accuracy without running the benchmark
Simulating `accuracy = 0.99` is strictly prohibited. Use `"N/A - experiment not executed"`.

### Mistake 7: Confusing temporal and cross-modal pairs
Temporal = Time difference. Cross-modal = Sensor difference.

### Mistake 8: Loading a 10GB+ GeoTIFF entirely into RAM
Out Of Memory (OOM) error. Use Rasterio metadata and windowed tile extraction.

### Mistake 9: Assuming a bounding box from a VLM is automatically geospatial coordinates
VLMs output *pixel bounds*. They must be mathematically warped by the image's `affine transform` to become *geospatial coordinates* (lat/lon).

### Mistake 10: Treating model confidence as certainty
Softmax is often overconfident. Always provide the spatial evidence.

---

## 25. SatQuery Glossary

- **Agentic workflow**: Automated routing of tasks to specialized models based on user intent.
- **Backscatter**: Radar signal reflected directly back to the sensor.
- **Band**: A discrete slice of the electromagnetic spectrum.
- **Bounding box**: Min/max coordinates defining an area of interest.
- **CROMA**: Contrastive Remote Sensing Representations model (foundation model for SAR/Optical).
- **CRS**: Coordinate Reference System. Maps pixels to Earth locations.
- **dB**: Decibels, a logarithmic scale used for SAR backscatter values.
- **GeoTIFF**: Standard image format storing pixels alongside geospatial metadata.
- **Grounding**: The AI process of linking a textual concept (e.g., "ship") to a specific spatial bounding box.
- **Multispectral**: Imagery combining multiple distinct bands of light (e.g., visible and infrared).
- **Nodata**: Pixel values marking empty/invalid areas, usually around borders.
- **Optical**: Sensors relying on sunlight reflected off the Earth.
- **Pretrained model**: A neural network already trained on massive datasets, ready for fine-tuning or feature extraction.
- **SAR**: Synthetic Aperture Radar.
- **Temporal pair**: Two images of the same location taken at different times.
- **Tile**: A small, processed chunk of a massive satellite image.
- **VLM**: Vision-Language Model. Combines image processing with natural language generation.
- **VQA**: Visual Question Answering.

---

## 26. "If You Only Remember 10 Things"

```text
1. Optical measures reflected sunlight/radiation.
2. SAR actively emits radar and measures structural backscatter.
3. Multispectral images contain multiple invisible spectral bands.
4. SAR is NOT an RGB photograph.
5. Temporal pairs compare the same location at different times.
6. Cross-modal pairs combine different sensor modalities at the same time.
7. Co-registration is the mandatory spatial alignment of pixels.
8. CROMA creates joint mathematical representations, not text.
9. VLMs (like GeoChat) combine visual features with language generation.
10. SatQuery routes queries to specialists and always returns evidence.
```

---

## 27. Learning Resources

- **CROMA Paper/Repo**: [GitHub - antofuller/CROMA](https://github.com/antofuller/CROMA) | *Authoritative source for the foundation model.*
- **GeoChat**: [GitHub - MBZUAI-Gradio/GeoChat](https://github.com/mbzuai-oryx/GeoChat) | *Authoritative VLM for remote sensing.*
- **BigEarthNet**: [BigEarthNet Archive](https://bigearth.net/) | *Authoritative multimodal dataset source.*
- **Copernicus Sentinel Data**: [ESA Sentinel Online](https://sentinels.copernicus.eu/) | *Official documentation for S1 and S2.*
- **Rasterio Documentation**: [Rasterio](https://rasterio.readthedocs.io/) | *Standard library for geospatial raster processing.*

---

## 28. Project-Specific vs General Knowledge

- **GENERAL CONCEPT**: Describes how the science or AI architecture broadly works.
- **SATQUERY IMPLEMENTATION**: Describes exactly how this repository uses it today.

*Example:*
**GENERAL:** "CROMA generates multimodal representations using a Vision Transformer."
**SATQUERY:** "SatQuery currently uses `CROMA-base` through `engine/models/croma.py`, explicitly mapping its `joint_GAP` to a lightweight downstream LinearProbe for Water/Built-up classification."

This separation ensures the core learning concepts remain valid even if the underlying code is updated tomorrow.

---

## 29. Update History

| Day | Update |
|---|---|
| Day 10/11 | Initial learning guide created; remote sensing, SAR, temporal imagery, CROMA, datasets, VLMs, geospatial concepts documented |

---

## 30. Future Update Rule

> Before completing each future development day, inspect the day's code, model research, datasets, terminology, and architecture changes. If a new domain-specific concept was introduced, update this learning guide before committing the day's work.
