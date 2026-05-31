from rest_framework import viewsets, permissions, parsers, decorators, response
from .models import Design, DesignAsset
from .serializers import DesignSerializer, DesignAssetSerializer
from .tasks import generate_mockup_async


class DesignAssetViewSet(viewsets.ModelViewSet):
    serializer_class = DesignAssetSerializer
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)

    def get_queryset(self):
        return DesignAsset.objects.filter(user=self.request.user)


class DesignViewSet(viewsets.ModelViewSet):
    serializer_class = DesignSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Design.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @decorators.action(detail=True, methods=["post"])
    def render_mockup(self, request, pk=None):
        """Trigger async mockup generation."""
        design = self.get_object()
        generate_mockup_async.delay(str(design.id))
        return response.Response({"status": "queued"})

