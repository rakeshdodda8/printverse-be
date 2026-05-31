from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile, Address, SocialAccount, ImportedPhoto

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "email", "phone", "role",
            "is_email_verified", "is_phone_verified",
            "first_name", "last_name", "date_joined",
        )
        read_only_fields = ("id", "role", "is_email_verified", "is_phone_verified", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.CUSTOMER)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone", "role")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user, full_name=f"{user.first_name} {user.last_name}".strip())
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ("user",)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ("user",)


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ("id", "provider", "provider_user_id", "scopes", "created_at")


class ImportedPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportedPhoto
        fields = "__all__"
        read_only_fields = ("user",)


class SocialLoginSerializer(serializers.Serializer):
    """Generic social login payload from mobile clients."""

    provider = serializers.ChoiceField(choices=["google", "facebook", "instagram"])
    access_token = serializers.CharField()
    id_token = serializers.CharField(required=False, allow_blank=True)

