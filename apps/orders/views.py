import secrets
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, permissions, decorators, response, status, generics
from rest_framework.exceptions import ValidationError

from apps.common.permissions import IsAdminRole, IsVendor
from apps.products.models import Product, ProductVariant
from apps.users.models import Address
from apps.designs.models import Design
from apps.vendors.models import CommissionRule

from .models import Cart, CartItem, Coupon, Order, OrderItem, Shipment, OrderStatusHistory
from .serializers import (
    CartSerializer, CartItemSerializer, CouponSerializer, OrderSerializer,
    CheckoutSerializer, ShipmentSerializer,
)
from . import pricing
from apps.notifications.tasks import send_order_status_notification


def _generate_order_number() -> str:
    return "PV" + secrets.token_hex(5).upper()


def _get_or_create_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return _get_or_create_cart(self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart = _get_or_create_cart(self.request.user)
        variant = serializer.validated_data["variant"]
        product = serializer.validated_data["product"]
        unit_price = (product.base_price + variant.extra_price)
        serializer.save(cart=cart, unit_price=unit_price)


class CouponApplyView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CouponSerializer

    def post(self, request):
        code = request.data.get("code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            raise ValidationError({"code": "Invalid coupon"})
        cart = _get_or_create_cart(request.user)
        cart.coupon = coupon
        cart.save()
        return response.Response(CouponSerializer(coupon).data)


class CheckoutView(generics.GenericAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cart = _get_or_create_cart(request.user)
        if not cart.items.exists():
            raise ValidationError("Cart is empty")
        address = Address.objects.get(id=ser.validated_data["shipping_address_id"], user=request.user)

        coupon = None
        code = ser.validated_data.get("coupon_code", "")
        if code:
            coupon = Coupon.objects.filter(code=code.upper(), is_active=True).first()
        elif cart.coupon:
            coupon = cart.coupon

        lines = []
        items_data = []
        vendor = None
        for it in cart.items.select_related("product", "variant"):
            lines.append(pricing.LineInput(
                base_price=Decimal(it.product.base_price),
                print_cost=Decimal(it.product.print_cost) if it.design else Decimal("0"),
                color_extra=Decimal(it.variant.extra_price),
                quantity=it.quantity,
            ))
            items_data.append(it)
            if vendor is None and it.product.vendor:
                vendor = it.product.vendor

        commission = None
        if vendor:
            rule = getattr(vendor, "commission", None)
            commission = rule.percent if rule else None

        result = pricing.compute(lines, coupon=coupon, commission_percent=commission)

        order = Order.objects.create(
            user=request.user,
            vendor=vendor,
            order_number=_generate_order_number(),
            shipping_address=address,
            subtotal=result.subtotal,
            print_cost_total=result.print_cost_total,
            color_charges=result.color_charges,
            shipping=result.shipping,
            tax=result.tax,
            discount=result.discount,
            total=result.total,
            commission_percent=result.commission_percent,
            commission_amount=result.commission_amount,
            vendor_payout=result.vendor_payout,
            coupon=coupon,
            customer_accepted_non_returnable=True,
            notes=ser.validated_data.get("notes", ""),
        )

        for it, line_total in zip(items_data, result.line_totals):
            OrderItem.objects.create(
                order=order,
                product=it.product,
                variant=it.variant,
                design=it.design,
                quantity=it.quantity,
                unit_price=it.unit_price,
                print_cost=it.product.print_cost if it.design else Decimal("0"),
                line_total=line_total,
            )

        OrderStatusHistory.objects.create(order=order, status=order.status, changed_by=request.user, note="Order placed")
        cart.items.all().delete()
        cart.coupon = None
        cart.save()

        return response.Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ("admin", "superadmin"):
            return Order.objects.all().prefetch_related("items", "status_history")
        if user.role == "vendor":
            return Order.objects.filter(vendor__user=user).prefetch_related("items", "status_history")
        return Order.objects.filter(user=user).prefetch_related("items", "status_history")

    @decorators.action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(Order.Status.choices):
            raise ValidationError({"status": "Invalid status"})

        role = request.user.role
        # Customers can only flip their own order from "pending" → "accepted"
        # to simulate a successful payment in the demo build.
        if role == "customer":
            if order.user_id != request.user.id or new_status != Order.Status.ACCEPTED \
                    or order.status != Order.Status.PENDING:
                return response.Response({"detail": "Forbidden"}, status=403)
        elif role not in ("vendor", "admin", "superadmin"):
            return response.Response({"detail": "Forbidden"}, status=403)

        order.status = new_status
        order.save(update_fields=["status"])
        OrderStatusHistory.objects.create(order=order, status=new_status, changed_by=request.user)
        send_order_status_notification.delay(str(order.id), new_status)
        return response.Response(OrderSerializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="tracking")
    def tracking(self, request, pk=None):
        order = self.get_object()
        shipment, _ = Shipment.objects.update_or_create(
            order=order,
            defaults={
                "courier": request.data.get("courier", ""),
                "tracking_number": request.data.get("tracking_number", ""),
                "tracking_url": request.data.get("tracking_url", ""),
            },
        )
        return response.Response(ShipmentSerializer(shipment).data)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminRole()]

