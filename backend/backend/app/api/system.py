import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.dependencies import get_settings
from app.schemas.system import CapabilitiesResponse, HealthResponse

router = APIRouter(prefix="/api/v1", tags=["system"])

ALL_TASKS = [
    "single_image_vqa",
    "single_image_caption",
    "single_image_grounding",
    "temporal_change_detection",
    "temporal_change_description",
    "temporal_change_vqa",
    "cross_modal_optical_sar",
    "croma_classification",
]

ALL_INPUT_TYPES = [
    "single_optical",
    "single_multispectral",
    "single_sar",
    "temporal_optical",
    "temporal_sar",
    "optical_sar_pair",
]


@router.get("/health", response_model=HealthResponse)
def health(settings=Depends(get_settings)):
    engine_available = False
    try:
        from engine import SatQueryEngine  # noqa: F401

        engine_available = True
    except Exception:
        pass

    torch_available = False
    cuda_available = False
    try:
        import torch

        torch_available = True
        cuda_available = torch.cuda.is_available()
    except Exception:
        pass

    croma_available = False
    try:
        from engine.models.croma.specialist import CROMASpecialist  # noqa: F401

        croma_available = True
    except Exception:
        pass

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        engine_mode=os.getenv("SATQUERY_MODEL_MODE", settings.SATQUERY_MODEL_MODE),
        engine_available=engine_available,
        torch_available=torch_available,
        cuda_available=cuda_available,
        croma_available=croma_available,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/capabilities", response_model=CapabilitiesResponse)
def capabilities(settings=Depends(get_settings)):
    return CapabilitiesResponse(
        tasks=ALL_TASKS,
        input_types=ALL_INPUT_TYPES,
        supported_formats=["GeoTIFF"],
        max_upload_bytes=settings.max_upload_bytes,
        models={
            "mock": ["MockVQA", "MockCaptioner", "MockGrounding", "baseline_change_detector", "optical_sar_specialist"],
            "real": ["remote_sensing_vqa", "remote_sensing_grounding", "croma_specialist"],
        },
        engine_mode=os.getenv("SATQUERY_MODEL_MODE", settings.SATQUERY_MODEL_MODE),
    )
