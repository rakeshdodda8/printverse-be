from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("profiles", views.VendorProfileViewSet, basename="vendor-profile")
router.register("commissions", views.CommissionRuleViewSet, basename="commission")
router.register("payouts", views.PayoutViewSet, basename="payout")

urlpatterns = router.urls

