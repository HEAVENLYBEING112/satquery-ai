import os
import uuid
import shutil
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

# Add root to sys.path to import engine
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.core import SatQueryEngine
from engine.contracts import InputBundle, ImageAsset, TaskType, EngineResult, EvidenceBundle, SpecialistResult

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SatQuery AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine globally
engine = SatQueryEngine()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_modality(filename: str) -> str:
    # A simple heuristic based on typical SatQuery usage
    name = filename.lower()
    if "sar" in name:
        return "sar"
    return "optical"

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "SatQuery Backend is running"}

@app.post("/analyze")
async def analyze(
    query: str = Form(...),
    files: List[UploadFile] = File(...),
    modalities: List[str] = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="Missing image files")
        
    if len(files) > 2:
        raise HTTPException(status_code=400, detail="Maximum of 2 images supported")

    images = []
    written_files = []
    
    try:
        for i, upload in enumerate(files):
            if not upload.filename:
                continue
                
            ext = Path(upload.filename).suffix.lower()
            if ext not in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
                raise HTTPException(status_code=400, detail=f"Unsupported file type.")
                
            file_id = str(uuid.uuid4())
            save_path = UPLOAD_DIR / f"{file_id}_{upload.filename}"
            
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)
            written_files.append(str(save_path.absolute()))
                
            # Use RasterLoader to parse metadata and enforce security limits
            from engine.geospatial.loader import RasterLoader
            loader = RasterLoader()
            # The loader will throw RasterLoaderError on corrupt files or oversized dimensions
            try:
                modality_override = None
                if modalities and i < len(modalities) and modalities[i]:
                    modality_override = modalities[i].lower()
                asset = loader.load(str(save_path.absolute()), modality_override=modality_override)
            except Exception as e:
                import logging
                logging.error(f"Image validation failed: {str(e)}")
                raise HTTPException(status_code=400, detail="Image validation failed. The file may be corrupt, unsupported, or excessively large.")
            
            # Keep original filename for client reference
            asset.filename = upload.filename
            asset.id = file_id
            images.append(asset)
            
        bundle = InputBundle(images=images)
        
        try:
            result = engine.analyze(bundle, query)
        except Exception as e:
            # Prevent stack trace and filesystem path leakage
            import logging
            logging.error(f"Backend Exception: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")
    finally:
        # Cleanup uploaded files safely regardless of where failure occurred
        for filepath in written_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass
        
    # Serialize result preserving all engine information
    
    def serialize_evidence(evidence: EvidenceBundle) -> Dict[str, Any]:
        return {
            "textual_evidence": evidence.textual_evidence,
            "bounding_boxes": [
                {
                    "label": b.label,
                    "coordinates": b.coordinates,
                    "confidence": b.confidence,
                    "source": b.source
                } for b in evidence.bounding_boxes
            ],
            "visualizations": evidence.visualizations,
            "change_statistics": evidence.change_statistics,
            "change_mask": {
                "width": evidence.change_mask.width,
                "height": evidence.change_mask.height,
                "mask_path": evidence.change_mask.mask_path,
                "threshold_used": evidence.change_mask.threshold_used,
                "changed_pixel_count": evidence.change_mask.changed_pixel_count,
                "changed_fraction": evidence.change_mask.changed_fraction,
            } if evidence.change_mask else None,
            "metadata": evidence.metadata
        }
        
    def serialize_specialist(sp: SpecialistResult) -> Dict[str, Any]:
        return {
            "status": sp.status,
            "model_name": sp.model_name,
            "task": sp.task,
            "answer": sp.answer,
            "confidence": sp.confidence,
            "evidence": serialize_evidence(sp.evidence) if sp.evidence else None,
            "metadata": sp.metadata,
            "execution_time": sp.execution_time,
            "error": sp.error
        }

    response_data = {
        "request_id": result.request_id,
        "status": result.status,
        "query": result.query,
        "task": result.task,
        "answer": result.answer,
        "confidence": result.confidence,
        "specialist_results": [serialize_specialist(sr) for sr in result.specialist_results],
        "evidence": [serialize_evidence(e) for e in result.evidence],
        "execution_trace": result.execution_trace,
        "errors": [{"code": err.code, "message": err.message} for err in result.errors]
    }
    
    # If the engine failed during planning or validation, it might return status="failed"
    status_code = 400 if result.status == "failed" else 200
    
    return JSONResponse(status_code=status_code, content=response_data)
