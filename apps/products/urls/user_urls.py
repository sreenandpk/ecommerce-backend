from django.urls import path
from apps.products.views.user_views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
)

urlpatterns = [
    # CATEGORY (USER)
    path("categories/", CategoryListView.as_view()),

    # PRODUCT (USER)
    path("products/", ProductListView.as_view()),
    path("products/<slug:slug>/", ProductDetailView.as_view()),
]
