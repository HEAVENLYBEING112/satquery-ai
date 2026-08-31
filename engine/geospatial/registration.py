from engine.contracts import ImageAsset

class RegistrationResult:
    def __init__(self, status: str, reason: str = ""):
        self.status = status
        self.reason = reason

def register_images(image_a: ImageAsset, image_b: ImageAsset) -> RegistrationResult:
    """Interface for image registration."""
    if image_a.crs == image_b.crs and image_a.resolution == image_b.resolution and image_a.bbox == image_b.bbox:
        return RegistrationResult(status="not_required", reason="Images are already perfectly aligned.")
    return RegistrationResult(status="required", reason="Registration required based on spatial differences.")
