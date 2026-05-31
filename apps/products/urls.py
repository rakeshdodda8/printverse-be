from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("items", views.ProductViewSet, basename="product")
router.register("reviews", views.ReviewViewSet, basename="review")
router.register("wishlist", views.WishlistViewSet, basename="wishlist")

urlpatterns = router.urls

