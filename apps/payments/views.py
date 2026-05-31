from django.http import HttpResponse, JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from .models import Payment
from .serializers import (
    PaymentSerializer, RazorpayCreateSerializer, RazorpayVerifySerializer,
    StripeCreateSerializer,
)
from .gateways import RazorpayGateway, StripeGateway
from .invoices import generate_invoice_pdf


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


class RazorpayCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = RazorpayCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = Order.objects.get(id=ser.validated_data["order_id"], user=request.user)
        gw = RazorpayGateway()
        rp_order = gw.create_order(order.total, "INR", receipt=order.order_number)
        payment = Payment.objects.create(
            order=order, gateway=Payment.Gateway.RAZORPAY,
            gateway_order_id=rp_order["id"], amount=order.total,
            currency="INR", raw_response=rp_order,
        )
        return Response({
            "payment_id": str(payment.id),
            "razorpay_order_id": rp_order["id"],
            "amount": rp_order["amount"],
            "currency": rp_order["currency"],
            "key": __import__("django").conf.settings.RAZORPAY_KEY_ID,
        })


class RazorpayVerifyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = RazorpayVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        gw = RazorpayGateway()
        if not gw.verify_signature(d["razorpay_order_id"], d["razorpay_payment_id"], d["razorpay_signature"]):
            return Response({"detail": "Invalid signature"}, status=400)
        try:
            payment = Payment.objects.get(gateway_order_id=d["razorpay_order_id"])
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found"}, status=404)
        payment.gateway_payment_id = d["razorpay_payment_id"]
        payment.status = Payment.Status.CAPTURED
        payment.save()
        payment.order.status = Order.Status.ACCEPTED
        payment.order.save(update_fields=["status"])
        return Response(PaymentSerializer(payment).data)


class StripeCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = StripeCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = Order.objects.get(id=ser.validated_data["order_id"], user=request.user)
        gw = StripeGateway()
        intent = gw.create_payment_intent(order.total, ser.validated_data["currency"],
                                          metadata={"order_number": order.order_number})
        payment = Payment.objects.create(
            order=order, gateway=Payment.Gateway.STRIPE,
            gateway_order_id=intent.id, amount=order.total,
            currency=ser.validated_data["currency"].upper(), raw_response=intent,
        )
        return Response({
            "payment_id": str(payment.id),
            "client_secret": intent.client_secret,
            "publishable_key_hint": "Use your Stripe publishable key on the client",
        })


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = StripeGateway().construct_event(payload, sig)
    except Exception as e:
        return Response({"detail": str(e)}, status=400)
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        Payment.objects.filter(gateway_order_id=intent["id"]).update(status=Payment.Status.CAPTURED)
    return Response({"received": True})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def invoice_pdf(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    pdf = generate_invoice_pdf(order)
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="invoice-{order.order_number}.pdf"'
    return resp

