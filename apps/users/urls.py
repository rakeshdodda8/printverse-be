from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register("addresses", views.AddressViewSet, basename="address")
router.register("social-accounts", views.SocialAccountViewSet, basename="social-account")
router.register("imported-photos", views.ImportedPhotoViewSet, basename="imported-photo")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("social/", views.SocialLoginView.as_view(), name="social-login"),
    path("me/", views.MeView.as_view(), name="me"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("fcm-token/", views.update_fcm_token, name="fcm-token"),
    path("social/facebook/sync-photos/", views.sync_facebook_photos, name="fb-sync"),
    path("social/instagram/sync-media/", views.sync_instagram_media, name="ig-sync"),
    path("", include(router.urls)),
]

