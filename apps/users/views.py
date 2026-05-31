from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Address, ImportedPhoto, Profile, SocialAccount
from .serializers import (
    AddressSerializer, ImportedPhotoSerializer, ProfileSerializer,
    RegisterSerializer, SocialAccountSerializer, SocialLoginSerializer,
    UserSerializer,
)
from . import social as social_auth

User = get_user_model()


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user).data, "tokens": _tokens_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=400)
        return Response(status=205)


class SocialLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        ser = SocialLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        provider = ser.validated_data["provider"]
        token = ser.validated_data["access_token"]
        try:
            if provider == "google":
                user = social_auth.authenticate_google(token, ser.validated_data.get("id_token", ""))
            elif provider == "facebook":
                user = social_auth.authenticate_facebook(token)
            else:
                user = social_auth.authenticate_instagram(token)
        except social_auth.SocialAuthError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"user": UserSerializer(user).data, "tokens": _tokens_for_user(user)})


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SocialAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocialAccountSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)


class ImportedPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ImportedPhotoSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = ImportedPhoto.objects.filter(user=self.request.user)
        source = self.request.query_params.get("source")
        return qs.filter(source=source) if source else qs


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_facebook_photos(request):
    try:
        photos = social_auth.fetch_facebook_photos(request.user)
    except social_auth.SocialAuthError as e:
        return Response({"detail": str(e)}, status=400)
    return Response(ImportedPhotoSerializer(photos, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_instagram_media(request):
    try:
        photos = social_auth.fetch_instagram_media(request.user)
    except social_auth.SocialAuthError as e:
        return Response({"detail": str(e)}, status=400)
    return Response(ImportedPhotoSerializer(photos, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    token = request.data.get("fcm_token", "")
    request.user.fcm_token = token
    request.user.save(update_fields=["fcm_token"])
    return Response({"ok": True})

