import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base with UUID PK + created/updated timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True)


class SoftDeleteModel(TimeStampedModel):
    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

