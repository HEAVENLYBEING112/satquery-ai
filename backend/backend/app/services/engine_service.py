"""InputBundle construction and engine invocation.

Hard constraints (SRS section 7):
- Never modify engine/, never duplicate its routing/registration/task-determination
  logic, never call anything but SatQueryEngine(...).analyze(input_bundle, query).
"""
import logging
import os
import threading
from pathlib import Path
from typing import Any

from app.serializers.engine_result import serialize_engine_result
from app.services.asset_service import ApiError

logger = logging.getLogger("satquery.engine")


class EngineUnavailableError(ApiError):
    def __init__(self, detail: str = "Engine is not importable"):
        super().__init__("ENGINE_UNAVAILABLE", 503, detail)


class AssetNotFoundError(ApiError):
    def __init__(self, asset_id: str):
        super().__init__("ASSET_NOT_FOUND", 404, f"Asset {asset_id} does not exist.")


def build_input_bundle(request, asset_store, job_output_dir: Path):
    """Builds engine.contracts.InputBundle from the API request + stored asset metadata.
    NEVER exposes server filesystem paths to the client — only the engine sees them."""
    from engine.contracts import ImageAsset, InputBundle  # deferred import: engine may be absent

    images = []
    asset_map: dict[str, Any] = {}

    for asset_ref in request.assets:
        stored = asset_store.get(asset_ref.asset_id)
        if not stored:
            raise AssetNotFoundError(asset_ref.asset_id)

        original_path = asset_store.get_original_file_path(asset_ref.asset_id)
        if original_path is None:
            raise AssetNotFoundError(asset_ref.asset_id)
        server_path = str(original_path)

        # BUG per SRS 6.2: determine_input_type() never returns SINGLE_MULTISPECTRAL.
        # Backend must set modality=optical for multispectral images so routing works.
        modality = "optical" if asset_ref.modality == "multispectral" else asset_ref.modality

        asset = ImageAsset(
            id=asset_ref.asset_id,
            path=server_path,
            filename=stored["filename"],
            format=stored.get("format", "GeoTIFF"),
            modality=modality,
            width=stored.get("width"),
            height=stored.get("height"),
            bands=stored.get("bands"),
            crs=stored.get("crs"),
            resolution=stored.get("resolution"),
            acquisition_time=asset_ref.acquisition_time,
            bbox=stored.get("bbox"),
            metadata=stored.get("raw_metadata", {}),
        )
        images.append(asset)
        asset_map[asset_ref.asset_id] = asset

    return InputBundle(images=images), asset_map


def is_engine_available() -> bool:
    try:
        from engine import SatQueryEngine  # noqa: F401

        return True
    except Exception:
        return False


def invoke_engine(job_id: str, request, asset_store, job_store, settings) -> None:
    """Runs in a worker thread — never on the FastAPI event loop."""
    try:
        job_store.update(job_id, status="running")

        job_output_dir = settings.jobs_dir / job_id / "output"
        job_output_dir.mkdir(parents=True, exist_ok=True)

        # NOTE: mutating process-wide os.environ is unsafe for concurrency in general.
        # It is acceptable here only because max_concurrent_jobs is pinned to 1.
        os.environ["SATQUERY_OUTPUT_DIR"] = str(job_output_dir)
        os.environ["SATQUERY_MODEL_MODE"] = settings.SATQUERY_MODEL_MODE

        bundle, asset_map = build_input_bundle(request, asset_store, job_output_dir)

        from engine import SatQueryEngine
        from engine.agent.registry import ModelRegistry

        engine = SatQueryEngine(registry=ModelRegistry())

        result_container: list = []
        err_container: list = []

        def run_engine():
            try:
                res = engine.analyze(bundle, request.query)
                result_container.append(res)
            except Exception as ex:  # noqa: BLE001
                err_container.append(ex)

        engine_thread = threading.Thread(target=run_engine, daemon=True)
        engine_thread.start()
        engine_thread.join(timeout=settings.job_timeout_seconds)

        if engine_thread.is_alive():
            # Python threads cannot be safely force-killed. Mark the job failed so the
            # client is not left hanging; the underlying thread may keep running.
            job_store.update(
                job_id, status="failed", error_message="ENGINE_TIMEOUT: Job exceeded time limit."
            )
            logger.critical("Job %s timed out; engine thread left running in background.", job_id)
            return

        if err_container:
            raise err_container[0]

        if not result_container:
            raise RuntimeError("ENGINE_NO_RESULT: Engine returned no result.")

        result = result_container[0]
        serialized = serialize_engine_result(result, job_id, asset_map, job_output_dir)

        fallback_triggered = any(
            eb.metadata.get("fallback_triggered") for eb in serialized.evidence if eb.metadata
        )
        if fallback_triggered:
            logger.warning("Job %s: engine fallback triggered.", job_id)

        job_store.update(
            job_id,
            status="completed" if result.status == "success" else "failed",
            result=serialized.model_dump(),
            engine_request_id=result.request_id,
        )

    except ApiError:
        raise
    except Exception as e:  # noqa: BLE001
        logger.error("Job %s failed: %s", job_id, e, exc_info=True)
        job_store.update(job_id, status="failed", error_message=f"INTERNAL_ERROR: {e}")
    finally:
        os.environ.pop("SATQUERY_OUTPUT_DIR", None)
