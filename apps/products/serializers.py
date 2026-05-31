from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant, Review, WishlistItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image_url", "alt", "sort_order")


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ("id", "size", "color_name", "color_hex", "sku", "stock", "extra_price")


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "base_price", "rating", "review_count",
            "is_featured", "is_trending", "is_new_arrival", "is_best_seller",
            "gender", "category", "primary_image",
        )

    def get_primary_image(self, obj):
        img = obj.images.order_by('sort_order').first()
        return img.image_url if img else None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_primary_image(self, obj):
        img = obj.images.order_by('sort_order').first()
        return img.image_url if img else None


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("user",)


class WishlistItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "product", "product_detail", "created_at")
        read_only_fields = ("user",)

