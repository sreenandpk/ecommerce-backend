from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import Product, Category, Ingredient, Allergen, City
from ..serializers.admin_serializers import (
    AdminProductSerializer,
    AdminCategorySerializer,
    IngredientSerializer,
    AllergenSerializer,
    CitySerializer,
)


# ================= CATEGORY (ADMIN) =================
class AdminCategoryListView(ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


class AdminCategoryCreateView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


class AdminCategoryUpdateView(UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "slug"


class AdminCategoryDeleteView(DestroyAPIView):
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


# ================= HELPER DROPDOWNS (ADMIN) =================
class AdminIngredientListView(ListAPIView):
    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

class AdminAllergenListView(ListAPIView):
    queryset = Allergen.objects.all().order_by("name")
    serializer_class = AllergenSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

class AdminCityListView(ListAPIView):
    queryset = City.objects.all().order_by("name")
    serializer_class = CitySerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


# ================= PRODUCT (ADMIN) =================
class AdminProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]


class AdminProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class AdminProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


class AdminProductUpdateView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "slug"


class AdminProductDeleteView(DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "slug"
