from django.conf import settings
from django.db import models
from apps.common.models import TimeStampedModel


class VendorProfile(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        SUSPENDED = "suspended"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_profile")
    business_name = models.CharField(max_length=160)
    gst_number = models.CharField(max_length=32, blank=True)
    pan_number = models.CharField(max_length=16, blank=True)
    bank_account_name = models.CharField(max_length=160, blank=True)
    bank_account_number = models.CharField(max_length=40, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.business_name


class CommissionRule(TimeStampedModel):
    """Configurable commission percentages assignable to a vendor or global default."""

    vendor = models.OneToOneField(VendorProfile, on_delete=models.CASCADE, related_name="commission", null=True, blank=True)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    is_default = models.BooleanField(default=False)
    notes = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.percent}% ({'default' if self.is_default else self.vendor})"


class Payout(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        PAID = "paid"
        FAILED = "failed"

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="payouts")
    period_start = models.DateField()
    period_end = models.DateField()
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=120, blank=True)

