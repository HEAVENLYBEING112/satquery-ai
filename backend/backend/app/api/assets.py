from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse

from app.dependencies import get_asset_store, get_settings
from app.schemas.assets import AssetUploadResponse
from app.schemas.errors import ApiErrorSchema
from app.services.asset_service import ApiError, AssetStore

router = APIRouter(prefix="/api/v1", tags=["assets"])

UPLOAD_ASSET_RESPONSES = {
    400: {
        "model": ApiErrorSchema,
        "description": "UNSUPPORTED_FORMAT (extension not in .tif/.tiff/.png/.jpg/.jpeg), INVALID_FILENAME "
        "(unsanitizable filename), or CORRUPT_FILE (rasterio could not read the upload).",
    },
    413: {"model": ApiErrorSchema, "description": "UPLOAD_TOO_LARGE — exceeds MAX_UPLOAD_BYTES."},
    422: {"model": ApiErrorSchema, "description": "VALIDATION_ERROR — request failed schema validation."},
    500: {"model": ApiErrorSchema, "description": "INTERNAL_SERVER_ERROR — unexpected failure."},
}

PREVIEW_RESPONSES = {
    404: {"model": ApiErrorSchema, "description": "ASSET_NOT_FOUND — unknown asset_id or no preview generated."},
}


@router.post(
    "/assets",
    response_model=AssetUploadResponse,
    status_code=200,
    responses=UPLOAD_ASSET_RESPONSES,
    summary="Upload a GeoTIFF asset",
)
async def upload_asset(file: UploadFile, asset_store: AssetStore = Depends(get_asset_store)):
    result = await asset_store.store(file)
    return AssetUploadResponse(**result)


@router.get(
    "/assets/{asset_id}/preview",
    responses={**PREVIEW_RESPONSES, 200: {"content": {"image/png": {}}, "description": "PNG preview image."}},
    summary="Fetch a PNG preview of an uploaded asset",
)
async def get_preview(asset_id: str, asset_store: AssetStore = Depends(get_asset_store)):
    stored = asset_store.get(asset_id)
    if not stored:
        raise ApiError("ASSET_NOT_FOUND", 404, f"Asset {asset_id} does not exist.")
    preview_path = asset_store.get_dir(asset_id) / "preview.png"
    if not preview_path.exists():
        raise ApiError("ASSET_NOT_FOUND", 404, "No preview available for this asset.")
    return FileResponse(str(preview_path), media_type="image/png")
