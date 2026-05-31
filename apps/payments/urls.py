from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("", views.PaymentViewSet, basename="payment")

urlpatterns = [
    path("razorpay/create/", views.RazorpayCreateView.as_view(), name="rzp-create"),
    path("razorpay/verify/", views.RazorpayVerifyView.as_view(), name="rzp-verify"),
    path("stripe/create/", views.StripeCreateView.as_view(), name="stripe-create"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe-webhook"),
    path("invoice/<uuid:order_id>/", views.invoice_pdf, name="invoice-pdf"),
    path("", include(router.urls)),
]

