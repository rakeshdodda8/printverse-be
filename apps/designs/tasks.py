from celery import shared_task
from .models import Design


@shared_task
def generate_mockup_async(design_id: str):
    """Generate mockup previews for a design. Placeholder for production rendering pipeline.

    A real implementation would composite the canvas JSON over a t-shirt template
    using Pillow / Skia / Headless Chromium and upload the rendered PNGs to S3.
    """
    try:
        design = Design.objects.get(id=design_id)
    except Design.DoesNotExist:
        return None
    previews = {}
    for area in (design.canvas or {}).keys():
        previews[area] = f"https://placehold.co/800x800?text={area}+mockup"
    design.preview_images = previews
    design.save(update_fields=["preview_images"])
    return previews

