from django.urls import path
from apps.products.views.admin_views import *

urlpatterns = [
    # CATEGORY
    path("admin/categories/", AdminCategoryListView.as_view()),
    path("admin/categories/create/", AdminCategoryCreateView.as_view()),
    path("admin/categories/<slug:slug>/update/", AdminCategoryUpdateView.as_view()),
    path("admin/categories/<slug:slug>/delete/", AdminCategoryDeleteView.as_view()),

    # DROPDOWNS
    path("admin/ingredients/", AdminIngredientListView.as_view()),
    path("admin/allergens/", AdminAllergenListView.as_view()),
    path("admin/cities/", AdminCityListView.as_view()),

    # PRODUCT
    path("admin/products/", AdminProductListView.as_view()),
    path("admin/products/create/", AdminProductCreateView.as_view()),
    path("admin/products/<slug:slug>/", AdminProductDetailView.as_view()),
    path("admin/products/<slug:slug>/update/", AdminProductUpdateView.as_view()),
    path("admin/products/<slug:slug>/delete/", AdminProductDeleteView.as_view()),
]
