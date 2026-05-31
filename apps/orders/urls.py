from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("cart-items", views.CartItemViewSet, basename="cart-item")
router.register("coupons", views.CouponViewSet, basename="coupon")
router.register("", views.OrderViewSet, basename="order")

urlpatterns = [
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/apply-coupon/", views.CouponApplyView.as_view(), name="apply-coupon"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("", include(router.urls)),
]

