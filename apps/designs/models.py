from django.db import models
from apps.common.models import TimeStampedModel
from apps.products.models import Product


class DesignAsset(TimeStampedModel):
    """Reusable image asset uploaded by user (gallery, camera, FB, IG)."""

    class Source(models.TextChoices):
        UPLOAD = "upload"
        CAMERA = "camera"
        FACEBOOK = "facebook"
        INSTAGRAM = "instagram"
        SAVED = "saved"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="design_assets")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.UPLOAD)
    file = models.FileField(upload_to="design_assets/%Y/%m/")
    url = models.URLField(blank=True)
    mime_type = models.CharField(max_length=80, blank=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    size_bytes = models.PositiveIntegerField(default=0)


class Design(TimeStampedModel):
    """A saved t-shirt design composition created in the studio."""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="designs")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="designs")
    name = models.CharField(max_length=120, default="Untitled Design")

    # The canvas JSON describes layers (image, text), positions, transforms.
    # Stored per print area: { "front": {...}, "back": {...}, ... }
    canvas = models.JSONField(default=dict)

    # Rendered mockup/preview images keyed by print area
    preview_images = models.JSONField(default=dict, blank=True)

    # Print-ready high-resolution flat files keyed by print area
    print_files = models.JSONField(default=dict, blank=True)

    is_template = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

