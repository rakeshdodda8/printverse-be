from django.db import models
from django.utils.text import slugify
from apps.common.models import TimeStampedModel
from apps.vendors.models import VendorProfile


class Category(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    image = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    class Gender(models.TextChoices):
        MEN = "men"
        WOMEN = "women"
        KIDS = "kids"
        UNISEX = "unisex"

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True)
    fabric = models.CharField(max_length=120, blank=True)
    gsm = models.PositiveIntegerField(default=180)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.UNISEX)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    print_cost = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    print_areas = models.JSONField(default=list, blank=True)  # ['front','back','left_sleeve','right_sleeve']
    delivery_days_min = models.PositiveIntegerField(default=4)
    delivery_days_max = models.PositiveIntegerField(default=8)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{str(self.id)[:8]}") if self.id else slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField()
    alt = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order",)


class ProductVariant(TimeStampedModel):
    SIZE_CHOICES = [(s, s) for s in ["XS", "S", "M", "L", "XL", "XXL", "3XL"]]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=8, choices=SIZE_CHOICES)
    color_name = models.CharField(max_length=40)
    color_hex = models.CharField(max_length=9, default="#FFFFFF")
    sku = models.CharField(max_length=64, unique=True)
    stock = models.PositiveIntegerField(default=0)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ("product", "size", "color_name")


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("product", "user")


class WishlistItem(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "product")

