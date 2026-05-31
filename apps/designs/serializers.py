from rest_framework import serializers
from .models import Design, DesignAsset


class DesignAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignAsset
        fields = "__all__"
        read_only_fields = ("user", "url", "mime_type", "width", "height", "size_bytes")

    def create(self, validated_data):
        from PIL import Image
        request = self.context["request"]
        instance = DesignAsset(user=request.user, **validated_data)
        if instance.file:
            try:
                with Image.open(instance.file) as im:
                    instance.width, instance.height = im.size
                    instance.mime_type = Image.MIME.get(im.format, "")
                instance.size_bytes = instance.file.size
            except Exception:
                pass
        instance.save()
        instance.url = instance.file.url if instance.file else ""
        instance.save(update_fields=["url"])
        return instance


class DesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = "__all__"
        read_only_fields = ("user", "preview_images", "print_files")

