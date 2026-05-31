import hashlib
import hmac
from decimal import Decimal
from django.conf import settings


class RazorpayGateway:
    """Thin wrapper around razorpay SDK. Falls back gracefully if not configured."""

    def __init__(self):
        import razorpay
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, amount: Decimal, currency: str = "INR", receipt: str = ""):
        amount_paise = int(Decimal(amount) * 100)
        return self.client.order.create({
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1,
        })

    def verify_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        body = f"{order_id}|{payment_id}".encode()
        secret = settings.RAZORPAY_KEY_SECRET.encode()
        expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


class StripeGateway:
    def __init__(self):
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe

    def create_payment_intent(self, amount: Decimal, currency: str = "usd", metadata: dict = None):
        amount_cents = int(Decimal(amount) * 100)
        return self.stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True},
        )

    def construct_event(self, payload, sig_header):
        return self.stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)

