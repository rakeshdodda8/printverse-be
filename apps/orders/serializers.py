from rest_framework import serializers
from .models import Cart, CartItem, Coupon, Order, OrderItem, Shipment, OrderStatusHistory
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer
from apps.designs.serializers import DesignSerializer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)
    variant_detail = ProductVariantSerializer(source="variant", read_only=True)
    design_detail = DesignSerializer(source="design", read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id", "product", "variant", "design", "quantity", "unit_price",
            "product_detail", "variant_detail", "design_detail",
        )
        read_only_fields = ("unit_price",)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    coupon_detail = CouponSerializer(source="coupon", read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "coupon", "coupon_detail", "updated_at")


class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)
    variant_detail = ProductVariantSerializer(source="variant", read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = "__all__"


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipment = ShipmentSerializer(read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = (
            "user", "order_number", "subtotal", "print_cost_total", "color_charges",
            "shipping", "tax", "discount", "total", "commission_percent",
            "commission_amount", "vendor_payout", "status",
        )


class CheckoutSerializer(serializers.Serializer):
    shipping_address_id = serializers.UUIDField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    accept_non_returnable = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_accept_non_returnable(self, v):
        if not v:
            raise serializers.ValidationError("You must accept the non-returnable products notice.")
        return v

