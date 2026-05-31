from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("status", "raw_response", "gateway_payment_id")


class RazorpayCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()


class RazorpayVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class StripeCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    currency = serializers.CharField(default="usd")

