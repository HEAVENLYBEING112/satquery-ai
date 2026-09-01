# 🛰️ SatQuery AI — Backend

> **Agentic Remote-Sensing Intelligence Backend**

SatQuery AI is a national-level hackathon project that enables users to analyze remote-sensing imagery through natural-language queries.

This branch contains the **Backend implementation** of SatQuery AI.

The backend acts as the bridge between the frontend application and the stabilized SatQuery Engine V1.

---

# 👨‍💻 Backend Developers

***Developers:*** `Tarunika , Subhiksha`

> Replace the placeholders above with the actual names of the two assigned backend developers.

Both developers are responsible for implementing the backend according to the official Backend Software Requirements Specification (SRS).

The two developers should coordinate changes on the same backend branch and keep the implementation continuously mergeable.

---

# 📋 Backend SRS

The complete backend requirements are maintained in:

**[`docs/backend-srs.md`](docs/backend-srs.md)**

The Backend SRS is the **primary and authoritative development specification** for this branch.

It defines:

- Backend architecture
- FastAPI application structure
- REST API contracts
- Request and response schemas
- Image upload handling
- GeoTIFF/TIFF validation
- Geospatial metadata extraction
- Asset storage
- Job creation and lifecycle
- Background execution
- Engine V1 integration
- Model/fallback handling
- Evidence serialization
- Preview generation
- Error handling
- Security requirements
- Configuration
- Logging
- Testing
- Docker/deployment requirements
- Acceptance criteria
- Git and merge requirements

### ⚠️ Important

**Read `docs/backend-srs.md` completely before implementing backend functionality.**

Do not create a second interpretation of the architecture.

If something is unclear, first check:

1. `docs/backend-srs.md`
2. `docs/engine-v1.md`
3. `docs/architecture.md`

Do not modify Engine V1 simply to make the backend implementation easier.

---

# 🏗️ Backend's Position in SatQuery AI

The backend sits between the user-facing frontend and the SatQuery Engine.

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │    FRONTEND     │
                  │   feat/frontend │
                  └────────┬────────┘
                           │
                           │ REST / HTTP
                           ▼
                  ┌─────────────────┐
                  │     BACKEND     │
                  │   feat/backend  │
                  │                 │
                  │    FastAPI      │
                  └────────┬────────┘
                           │
                           │ Engine API
                           ▼
                  ┌─────────────────┐
                  │   SATQUERY      │
                  │    ENGINE V1    │
                  │ feat/engine-core│
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
             VQA        TEMPORAL     OPTICAL +
          GROUNDING       CHANGE         SAR
              │            │            │
              └────────────┼────────────┘
                           ▼
                    EvidenceBundle
                           │
                           ▼
                      EngineResult
                           │
                           ▼
                      BACKEND API
                           │
                           ▼
                       FRONTEND
