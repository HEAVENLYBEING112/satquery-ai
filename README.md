# SatQuery AI – Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries

[![React](https://img.shields.io/badge/Frontend-React%2018-38BDF8?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript%205.8-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Bundler-Vite%208-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vite.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS%20v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Organization](https://img.shields.io/badge/Organization-ISRO%20SAC-FF9933?style=flat-square&logo=satellite&logoColor=white)](https://www.isro.gov.in/)
[![Theme](https://img.shields.io/badge/Theme-Space%20Technology-0EA5E9?style=flat-square)](https://github.com/sujans9b-sys/satquery-ai)
[![GitHub Pages](https://img.shields.io/badge/Deployment-GitHub%20Pages-22C55E?style=flat-square&logo=githubpages&logoColor=white)](https://sujans9b-sys.github.io/satquery-ai/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-sujans9b--sys%2Fsatquery--ai-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/sujans9b-sys/satquery-ai)

---

## 🔗 Project Quick Links

- 🛰️ **Virtual Demo**: [https://sujans9b-sys.github.io/satquery-ai/](https://sujans9b-sys.github.io/satquery-ai/) *(Demo Web Application)*
- 📂 **GitHub Repository**: [https://github.com/sujans9b-sys/satquery-ai](https://github.com/sujans9b-sys/satquery-ai)
- 📑 **System Requirements Specification (SRS)**: [`docs/frontend-srs.md`](docs/frontend-srs.md)

---

## 📖 System Overview

**SatQuery AI** is an advanced Mission-Control grade Vision-Language platform engineered to bridge the domain gap between generic Large Vision-Language Models (VLMs) and operational Remote Sensing (RS) satellite data. 

Through natural language text queries, analysts, scientists, and defense planners can interrogate complex multi-sensor Earth observation rasters (Optical VNIR and SAR Synthetic Aperture Radar) without needing manual GIS workflows, band math scripting, or specialist model selection.

---

## 🛰️ Key Capabilities & Scientific Workflows

### 1. 🔍 Single-Image Intelligence
- **Remote Sensing Visual Question Answering (RS-VQA)**: Interrogate land cover, object densities, and environmental conditions in plain English.
- **Scene Description**: Generate comprehensive, multi-paragraph spatial descriptions covering spectral features, topography, and human infrastructure.
- **Text-Guided Region Grounding**: Locate targets (e.g. *“Highlight docking vessels and cargo storage facilities”*) with precision bounding boxes and coordinate metadata.

### 2. 🔄 Multitemporal Change Analysis
- **Bi-Temporal Difference Mapping ($T_1$ vs $T_2$)**: Compare satellite observations across acquisition dates to quantify urban sprawl, deforestation, and flood inundation.
- **Interactive Curtain Swipe Slider**: Visual wipe comparison between pre-event and post-event raster imagery.
- **Quantitative Change Metrics**: Automated surface change percentage calculation (`Built-Up: +18%`, `Vegetation: -12%`).

### 3. 📡 Cross-Modal Optical + SAR Synergy
- **Complementary Sensor Fusion**: Joint analysis combining VNIR optical reflectance (NDVI, true-color textures) with cloud-penetrating Synthetic Aperture Radar (SAR) C-Band backscatter.
- **All-Weather Telemetry**: Uninterrupted day/night and all-weather intelligence even under cloud cover and monsoon precipitation.

### 4. 🤖 Agentic Orchestration & Auditability
- **Dynamic Task Routing**: Automatically inspects query intent, raster bounds, and sensor metadata to route tasks to domain specialists.
- **Transparent Execution Trace**: Step-by-step audit logs capturing router decisions, fallback triggers, and inference latency.
- **Strict Evidence Standards**: Unambiguous confidence reporting (`Confidence: N/A` for deterministic baseline models; never fabricated).

---

## 🎨 Space Technology Mission Control Design System

The user interface follows an **ISRO Mission Control Space Technology** aesthetic:
- **Primary Backgrounds**: Deep Space Black (`#050505`, `#090909`, `#0D0D0D`, `#111111`)
- **Typography**: Pure White (`#FFFFFF`) with Light Gray (`#A0A0A0`) and Muted Gray (`#666666`)
- **Primary Accent**: **Sky Blue (`#38BDF8`, `#0EA5E9`)** representing satellite communication, earth atmosphere, and AI elements.
- **Success Color**: **Green (`#22C55E`)** strictly reserved for `SYSTEM ONLINE`, `ENGINE READY`, and `COMPLETED`.
- **Error Color**: **Red (`#EF4444`)** strictly reserved for `FAILED`, `CRITICAL ERROR`, and system faults.

---

## 🔌 API-Ready Service Architecture

This frontend is designed to easily decouple and connect to backend APIs:

```
src/
├── api/
│   ├── client.ts              # Central Axios/Fetch client configured via VITE_API_BASE_URL
│   ├── assets.ts              # Asset upload API endpoints
│   ├── jobs.ts                # Job submission, status polling, and trace retrieval
│   ├── system.ts              # System health check & capabilities query
│   └── mock/                  # Deterministic simulation engine & fixtures
├── services/
│   ├── analysisService.ts     # Analysis workflow orchestration
│   ├── chatService.ts         # Conversational agent streaming adapter
│   └── reportService.ts       # Structured JSON & printable dossier generator
├── store/
│   └── useAppStore.ts         # Central Zustand state management
├── components/
│   ├── chat/                  # SatQuery conversational interface & quick commands
│   ├── viewer/                # Geospatial raster viewer & bounding box overlays
│   ├── upload/                # DropZone, asset cards & benchmark presets
│   ├── results/               # Analysis output, confidence badges & error panels
│   └── layout/                # Mission Control header & sidebar navigation
└── pages/                     # 10 dedicated platform pages
```

> **Future Backend Integration**: Simply set `VITE_USE_MOCK=false` in `.env` and configure `VITE_API_BASE_URL` to point to the real backend server.

---

## 🚀 Getting Started & Local Execution

### Prerequisites
- Node.js 18+ or 20+
- npm 9+ or pnpm

### Installation

```bash
# Clone repository
git clone https://github.com/sujans9b-sys/satquery-ai.git
cd satquery-ai

# Install dependencies
npm install

# Start local development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to launch the Mission Control workstation.

### Production Build

```bash
npm run build
```

The optimized static production bundle will be generated in the `dist/` directory.

---

## 🌐 Deployment to GitHub Pages

Whenever code is pushed to `main`:
1. The GitHub Action installs dependencies and executes `npm run build`.
2. The static bundle in `./dist` is published automatically to GitHub Pages.
3. The live application is immediately accessible at [https://sujans9b-sys.github.io/satquery-ai/](https://sujans9b-sys.github.io/satquery-ai/).

---

## 📄 License
Developed for ISRO Space Applications Centre (SAC) • Smart India Hackathon 2026.
