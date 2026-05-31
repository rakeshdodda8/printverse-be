"""Social authentication helpers — verify mobile-issued tokens with provider APIs."""
import requests
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SocialAccount, Profile, ImportedPhoto

User = get_user_model()


class SocialAuthError(Exception):
    pass


def _get_or_create_user(email, full_name, avatar=""):
    if not email:
        raise SocialAuthError("Email not provided by provider")
    user, created = User.objects.get_or_create(email=email, defaults={"is_email_verified": True})
    profile, _ = Profile.objects.get_or_create(user=user)
    if full_name and not profile.full_name:
        profile.full_name = full_name
    if avatar and not profile.avatar:
        profile.avatar = avatar
    profile.save()
    return user


def authenticate_google(access_token: str, id_token: str = "") -> User:
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        raise SocialAuthError("Invalid Google token")
    data = resp.json()
    user = _get_or_create_user(data.get("email"), data.get("name", ""), data.get("picture", ""))
    SocialAccount.objects.update_or_create(
        provider=SocialAccount.Provider.GOOGLE,
        provider_user_id=data["sub"],
        defaults={"user": user, "access_token": access_token, "raw_profile": data},
    )
    return user


def authenticate_facebook(access_token: str) -> User:
    resp = requests.get(
        "https://graph.facebook.com/me",
        params={"fields": "id,name,email,picture", "access_token": access_token},
        timeout=10,
    )
    if resp.status_code != 200:
        raise SocialAuthError("Invalid Facebook token")
    data = resp.json()
    picture = (data.get("picture") or {}).get("data", {}).get("url", "")
    user = _get_or_create_user(data.get("email"), data.get("name", ""), picture)
    SocialAccount.objects.update_or_create(
        provider=SocialAccount.Provider.FACEBOOK,
        provider_user_id=data["id"],
        defaults={"user": user, "access_token": access_token, "raw_profile": data,
                  "scopes": ["email", "public_profile", "user_photos"]},
    )
    return user


def authenticate_instagram(access_token: str) -> User:
    """Instagram Basic Display API. Email is typically not returned, so we synthesize one."""
    resp = requests.get(
        "https://graph.instagram.com/me",
        params={"fields": "id,username,account_type", "access_token": access_token},
        timeout=10,
    )
    if resp.status_code != 200:
        raise SocialAuthError("Invalid Instagram token")
    data = resp.json()
    synthetic_email = f"ig_{data['id']}@instagram.printverse.local"
    user = _get_or_create_user(synthetic_email, data.get("username", ""))
    SocialAccount.objects.update_or_create(
        provider=SocialAccount.Provider.INSTAGRAM,
        provider_user_id=data["id"],
        defaults={"user": user, "access_token": access_token, "raw_profile": data,
                  "scopes": ["user_profile", "user_media"]},
    )
    return user


def fetch_facebook_photos(user: User, limit: int = 50):
    """Pull user_photos via Graph API and persist as ImportedPhoto."""
    account = user.social_accounts.filter(provider=SocialAccount.Provider.FACEBOOK).first()
    if not account:
        raise SocialAuthError("Facebook account not linked")
    resp = requests.get(
        "https://graph.facebook.com/me/photos",
        params={
            "type": "uploaded",
            "fields": "id,images,name,created_time",
            "limit": limit,
            "access_token": account.access_token,
        },
        timeout=15,
    )
    items = resp.json().get("data", [])
    created = []
    for item in items:
        images = item.get("images") or []
        if not images:
            continue
        biggest = images[0]
        photo, _ = ImportedPhoto.objects.update_or_create(
            user=user,
            source="facebook",
            source_media_id=item["id"],
            defaults={
                "image_url": biggest["source"],
                "thumbnail_url": images[-1]["source"] if len(images) > 1 else biggest["source"],
                "caption": item.get("name", ""),
                "width": biggest.get("width", 0),
                "height": biggest.get("height", 0),
            },
        )
        created.append(photo)
    return created


def fetch_instagram_media(user: User, limit: int = 50):
    account = user.social_accounts.filter(provider=SocialAccount.Provider.INSTAGRAM).first()
    if not account:
        raise SocialAuthError("Instagram account not linked")
    resp = requests.get(
        "https://graph.instagram.com/me/media",
        params={
            "fields": "id,caption,media_type,media_url,thumbnail_url,timestamp",
            "limit": limit,
            "access_token": account.access_token,
        },
        timeout=15,
    )
    items = resp.json().get("data", [])
    created = []
    for item in items:
        if item.get("media_type") not in ("IMAGE", "CAROUSEL_ALBUM", "VIDEO"):
            continue
        photo, _ = ImportedPhoto.objects.update_or_create(
            user=user,
            source="instagram",
            source_media_id=item["id"],
            defaults={
                "image_url": item.get("media_url", ""),
                "thumbnail_url": item.get("thumbnail_url") or item.get("media_url", ""),
                "caption": item.get("caption", ""),
            },
        )
        created.append(photo)
    return created

