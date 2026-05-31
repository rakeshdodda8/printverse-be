from rest_framework import viewsets, permissions, decorators, response
from .models import VendorProfile, CommissionRule, Payout
from .serializers import VendorProfileSerializer, CommissionRuleSerializer, PayoutSerializer
from apps.common.permissions import IsAdminRole, IsVendor


class VendorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = VendorProfileSerializer
    queryset = VendorProfile.objects.all()

    def get_permissions(self):
        if self.action in ("list", "approve", "suspend"):
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        self.request.user.role = "vendor"
        self.request.user.save(update_fields=["role"])

    @decorators.action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        vp = self.get_object()
        vp.status = VendorProfile.Status.APPROVED
        vp.save()
        return response.Response({"status": vp.status})

    @decorators.action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        vp = self.get_object()
        vp.status = VendorProfile.Status.SUSPENDED
        vp.save()
        return response.Response({"status": vp.status})


class CommissionRuleViewSet(viewsets.ModelViewSet):
    queryset = CommissionRule.objects.all()
    serializer_class = CommissionRuleSerializer
    permission_classes = (IsAdminRole,)


class PayoutViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayoutSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("admin", "superadmin"):
            return Payout.objects.all()
        return Payout.objects.filter(vendor__user=user)

