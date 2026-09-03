# SatQuery AI - Backend API

The minimal backend exposes the SatQueryEngine via FastAPI.

## Endpoints

### 1. `GET /health`
Returns backend health status.
**Response**: `{"status": "ok", "message": "SatQuery Backend is running"}`

### 2. `POST /analyze`
Synchronous endpoint to analyze satellite imagery.
- **Form Data**:
  - `query` (str): The natural language query (e.g., "what is this?", "highlight buildings").
  - `files` (List[UploadFile]): 1-2 image files (PNG, JPG, TIFF).
- **Response** (200 OK):
  Returns a serialized `EngineResult` containing `status`, `task`, `answer`, `confidence`, `evidence`, etc.

**Error Responses**:
- `400 Bad Request`: Validation failure (e.g. missing files, engine validation error).
- `422 Unprocessable Entity`: Missing form parameters.
- `500 Internal Server Error`: Unhandled engine exception.

## Architecture
This is a thin wrapper over `SatQueryEngine.analyze()`. The backend does not implement workflow routing, caching, or asynchronous job processing. All workflows (VQA, Grounding, Temporal, Optical+SAR) are supported inherently by the engine contract.
