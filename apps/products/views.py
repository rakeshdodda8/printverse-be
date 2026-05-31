import django_filters
from rest_framework import viewsets, permissions, filters, decorators, response
from .models import Category, Product, Review, WishlistItem, ProductVariant
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer, ReviewSerializer, WishlistItemSerializer,
)


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")
    color = django_filters.CharFilter(field_name="variants__color_name", lookup_expr="iexact")
    size = django_filters.CharFilter(field_name="variants__size", lookup_expr="iexact")
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    category = django_filters.CharFilter(field_name="category__slug")

    class Meta:
        model = Product
        fields = ["gender", "is_featured", "is_trending", "is_new_arrival", "is_best_seller"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("sort_order", "name")
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images", "variants")
    permission_classes = (permissions.AllowAny,)
    filterset_class = ProductFilter
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend)
    search_fields = ("name", "description", "fabric")
    ordering_fields = ("base_price", "rating", "created_at")

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == "retrieve" else ProductListSerializer

    @decorators.action(detail=False)
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:20]
        return response.Response(ProductListSerializer(qs, many=True).data)

    @decorators.action(detail=False)
    def trending(self, request):
        qs = self.get_queryset().filter(is_trending=True)[:20]
        return response.Response(ProductListSerializer(qs, many=True).data)

    @decorators.action(detail=False, url_path="new-arrivals")
    def new_arrivals(self, request):
        qs = self.get_queryset().filter(is_new_arrival=True)[:20]
        return response.Response(ProductListSerializer(qs, many=True).data)

    @decorators.action(detail=False, url_path="best-sellers")
    def best_sellers(self, request):
        qs = self.get_queryset().filter(is_best_seller=True)[:20]
        return response.Response(ProductListSerializer(qs, many=True).data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

