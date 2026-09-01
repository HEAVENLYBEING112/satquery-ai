# 🛰️ SatQuery AI — Frontend

> **Agentic Vision-Language Assistant for Remote-Sensing Intelligence**

SatQuery AI is a national-level hackathon project designed to allow users to analyze remote-sensing imagery using natural-language queries.

This branch contains the **Frontend implementation** of SatQuery AI.

The frontend is responsible for providing an intuitive interface through which users can:

- Upload remote-sensing imagery
- Configure single-image, temporal, and optical-SAR workflows
- Enter natural-language queries
- Monitor analysis jobs
- View AI-generated answers
- Inspect spatial evidence and bounding boxes
- View image previews and overlays
- Inspect execution traces and model/fallback information
- Download generated evidence and reports

---

## 👨‍💻 Frontend Developer

**Developer:** `Sujan`

The developer is responsible for implementing the frontend according to the official Frontend Software Requirements Specification (SRS).

---

## 📋 Frontend SRS

The complete frontend requirements are maintained in:

**[`docs/frontend-srs.md`](docs/frontend-srs.md)**

The SRS is the **primary development specification** for this branch.

It defines:

- Frontend architecture
- UI/UX requirements
- Page structure
- Components
- State management
- API integration
- Upload workflows
- Job polling
- Remote-sensing workflow configuration
- Results visualization
- Bounding-box rendering
- Evidence handling
- Error handling
- Loading states
- Mock development mode
- Accessibility requirements
- Responsive behavior
- Testing requirements
- Acceptance criteria
- Git workflow
- Backend integration requirements

### ⚠️ Important

Do **not** invent backend APIs or change the Engine V1 architecture from the frontend.

If an API behavior is unclear, refer to the Backend SRS and coordinate with the backend developer.

---

# 🏗️ System Position

The frontend is one layer of the larger SatQuery AI system:

```text
                    USER
                     │
                     ▼
            ┌─────────────────┐
            │   SATQUERY UI   │
            │    FRONTEND     │
            └────────┬────────┘
                     │
                     │ REST API
                     ▼
            ┌─────────────────┐
            │     FASTAPI     │
            │     BACKEND     │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  SATQUERY       │
            │  ENGINE V1      │
            └────────┬────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       VQA /      Temporal    Optical +
      Grounding    Change        SAR
          │          │          │
          └──────────┼──────────┘
                     ▼
              EvidenceBundle
                     │
                     ▼
               EngineResult
                     │
                     ▼
                Backend API
                     │
                     ▼
                Frontend UI
