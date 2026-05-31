from django.db import models
from apps.common.models import TimeStampedModel
from apps.orders.models import Order


class Payment(TimeStampedModel):
    class Gateway(models.TextChoices):
        RAZORPAY = "razorpay"
        STRIPE = "stripe"

    class Status(models.TextChoices):
        CREATED = "created"
        AUTHORIZED = "authorized"
        CAPTURED = "captured"
        FAILED = "failed"
        REFUNDED = "refunded"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    gateway = models.CharField(max_length=20, choices=Gateway.choices)
    gateway_order_id = models.CharField(max_length=120, blank=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="INR")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    raw_response = models.JSONField(default=dict, blank=True)
    invoice_url = models.URLField(blank=True)
    receipt_url = models.URLField(blank=True)

