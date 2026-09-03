"""Asset upload, storage, metadata extraction and preview generation.

Contract (SRS section 20-22, extended):
- Extension allowlist: .tif / .tiff / .png / .jpg / .jpeg.
- Size enforced during streaming, before the whole file is buffered.
- Filename sanitized before any filesystem operation.
- rasterio.open() must succeed or the upload is rejected and deleted.
- Preview generation is best-effort and non-fatal.
- The original file is NEVER modified.

Non-GeoTIFF formats (PNG/JPEG) carry no embedded CRS or affine transform.
rasterio can still open them (pixel grid + band count are always available),
but `crs`, `resolution`, and `bbox` will be null for these uploads, and any
BoundingBox the engine later produces for that asset will resolve to
`coordinate_type: "pixel"` rather than `"geo"` (see determine_coordinate_type
in serializers/engine_result.py) — there is no CRS to project into. This is
expected, not a bug: without georeferencing there is no geographic frame to
express coordinates in.
"""
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Optional

from app.storage.filesystem import ensure_dir
from app.storage.paths import sanitize_filename

logger = logging.getLogger("satquery.assets")

# Maps a validated, lowercased extension to the format string reported in
# AssetUploadResponse.format and stored in ImageAsset.format for the engine.
FORMAT_BY_EXTENSION: dict[str, str] = {
    ".tif": "GeoTIFF",
    ".tiff": "GeoTIFF",
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
}


class ApiError(Exception):
    def __init__(self, code: str, status_code: int, message: Optional[str] = None):
        self.code = code
        self.status_code = status_code
        self.message = message or code
        super().__init__(self.message)


def extract_metadata(filepath: str) -> dict[str, Any]:
    """Extract raster metadata via rasterio. Raises on unreadable/corrupt files."""
    result: dict[str, Any] = {
        "width": None,
        "height": None,
        "bands": None,
        "crs": None,
        "resolution": None,
        "bbox": None,
        "raw_metadata": {},
    }
    import rasterio  # imported lazily so the rest of the backend works without it installed

    with rasterio.open(filepath) as src:
        result["width"] = src.width
        result["height"] = src.height
        result["bands"] = src.count
        result["crs"] = src.crs.to_string() if src.crs else None
        result["resolution"] = float(src.res[0]) if src.res else None
        result["bbox"] = list(src.bounds) if src.bounds else None
        result["raw_metadata"] = {
            "dtype": src.dtypes[0] if src.dtypes else None,
            "nodata": src.nodata,
        }
    return result


def generate_preview(src_path: str, dest_path: str, max_size: int = 512) -> None:
    """Convert a GeoTIFF/PNG/JPEG into a browser-viewable PNG thumbnail via rasterio,
    so the same percentile-stretch logic applies regardless of source format.
    Never touches the original file."""
    import numpy as np
    import rasterio
    from PIL import Image

    with rasterio.open(src_path) as src:
        bands = src.count
        scale = min(1.0, max_size / max(src.width, src.height))
        out_shape = (int(src.height * scale) or 1, int(src.width * scale) or 1)

        if bands >= 3:
            data = src.read([1, 2, 3], out_shape=(3, *out_shape))
        else:
            data = src.read([1], out_shape=(1, *out_shape))
            data = np.stack([data[0]] * 3)  # grayscale -> RGB

        nodata = src.nodata
        preview = np.zeros((3, data.shape[1], data.shape[2]), dtype=np.float32)
        for i in range(3):
            band = data[i].astype(np.float32)
            if nodata is not None:
                band[data[i] == nodata] = np.nan
            valid = band[~np.isnan(band)]
            if len(valid) == 0:
                continue
            lo, hi = np.percentile(valid, 2), np.percentile(valid, 98)
            if hi > lo:
                preview[i] = np.clip((band - lo) / (hi - lo), 0, 1)

        rgb = (np.transpose(preview, (1, 2, 0)) * 255).astype(np.uint8)
        img = Image.fromarray(rgb, mode="RGB")
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        img.save(dest_path, format="PNG", optimize=True)


class AssetStore:
    """Filesystem-backed store for uploaded assets: runtime/assets/{asset_id}/."""

    def __init__(self, settings):
        self.settings = settings
        ensure_dir(self.settings.assets_dir)

    def get_dir(self, asset_id: str) -> Path:
        return self.settings.assets_dir / asset_id

    def get_path(self, asset_id: str) -> Path:
        return self.get_dir(asset_id)

    def get_original_file_path(self, asset_id: str) -> Optional[Path]:
        """Path to the original uploaded file, whatever its extension.
        Prefer this over guessing `original.tif` — that hardcoded name broke
        as soon as PNG/JPEG uploads were allowed."""
        stored = self.get(asset_id)
        if not stored or "storage_filename" not in stored:
            return None
        return self.get_dir(asset_id) / stored["storage_filename"]

    def get(self, asset_id: str) -> Optional[dict[str, Any]]:
        meta_path = self.get_dir(asset_id) / "metadata.json"
        if not meta_path.exists():
            return None
        return json.loads(meta_path.read_text())

    async def store(self, file) -> "AssetUploadResult":
        settings = self.settings
        ext = Path(file.filename or "").suffix.lower()
        if ext not in settings.allowed_extensions:
            raise ApiError("UNSUPPORTED_FORMAT", 400, f"Extension {ext!r} is not supported")

        safe_name = sanitize_filename(file.filename or f"upload{ext}")

        asset_id = str(uuid.uuid4())
        asset_dir = self.get_dir(asset_id)
        ensure_dir(asset_dir)
        storage_filename = f"original{ext}"
        dest = asset_dir / storage_filename

        total_bytes = 0
        with dest.open("wb") as f:
            while True:
                chunk = await file.read(65536)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > settings.max_upload_bytes:
                    f.close()
                    dest.unlink(missing_ok=True)
                    raise ApiError("UPLOAD_TOO_LARGE", 413, "File exceeds MAX_UPLOAD_BYTES")
                f.write(chunk)

        try:
            metadata = extract_metadata(str(dest))
        except Exception:
            dest.unlink(missing_ok=True)
            raise ApiError("CORRUPT_FILE", 400, "File could not be read as a raster")

        preview_url = None
        try:
            preview_path = asset_dir / "preview.png"
            generate_preview(str(dest), str(preview_path))
            preview_url = f"/api/v1/assets/{asset_id}/preview"
        except Exception as e:  # non-fatal
            logger.warning("Preview generation failed for %s: %s", asset_id, e)

        meta = {
            "filename": safe_name,
            "storage_filename": storage_filename,
            "format": FORMAT_BY_EXTENSION[ext],
            "size_bytes": total_bytes,
            **metadata,
        }
        (asset_dir / "metadata.json").write_text(json.dumps(meta, default=str))

        return AssetUploadResult(asset_id=asset_id, preview_url=preview_url, **meta)


class AssetUploadResult(dict):
    """Lightweight holder so callers can both dict-access and attribute-access fields."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__ = self
