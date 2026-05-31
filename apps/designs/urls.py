from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("assets", views.DesignAssetViewSet, basename="design-asset")
router.register("", views.DesignViewSet, basename="design")

urlpatterns = router.urls

