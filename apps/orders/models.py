from django.db import models
from apps.common.models import TimeStampedModel
from apps.products.models import Product, ProductVariant
from apps.designs.models import Design
from apps.users.models import Address
from apps.vendors.models import VendorProfile


class Coupon(TimeStampedModel):
    class Type(models.TextChoices):
        FLAT = "flat"
        PERCENT = "percent"

    code = models.CharField(max_length=40, unique=True)
    type = models.CharField(max_length=10, choices=Type.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class Cart(TimeStampedModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="cart")
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        PRINTING = "printing"
        PACKED = "packed"
        SHIPPED = "shipped"
        OUT_FOR_DELIVERY = "out_for_delivery"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"
        REFUNDED = "refunded"

    user = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="orders")
    vendor = models.ForeignKey(VendorProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    order_number = models.CharField(max_length=24, unique=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)

    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    print_cost_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    color_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vendor_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    customer_accepted_non_returnable = models.BooleanField(default=False)
    notes = models.TextField(blank=True)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    design = models.ForeignKey(Design, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    print_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)


class Shipment(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    courier = models.CharField(max_length=80, blank=True)
    tracking_number = models.CharField(max_length=80, blank=True)
    tracking_url = models.URLField(blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)


class OrderStatusHistory(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=24)
    note = models.CharField(max_length=200, blank=True)
    changed_by = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL)

