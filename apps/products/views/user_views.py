from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Product, Category
from ..serializers.user_serializers import ProductSerializer, CategorySerializer


# ================= CATEGORY (USER) =================
class CategoryListView(ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# ================= PRODUCT BASE =================
class ProductBaseQuerysetMixin:
    def get_queryset(self):
        return (
            Product.objects
            .select_related("nutrition", "category")
            .prefetch_related(
                "ingredients",
                "allergens",
                "available_cities"
            )
            .filter(is_active=True)
        )


# ================= PRODUCT LIST =================
class ProductListView(ProductBaseQuerysetMixin, ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "currency",
        "category__slug",
        "stock",
    ]

    search_fields = [
        "name",
        "description",
        "story",
        "category__name",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "stock",
        "average_rating",
        "review_count",
    ]

    ordering = ["-created_at"]


# ================= PRODUCT DETAIL =================
class ProductDetailView(ProductBaseQuerysetMixin, RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"