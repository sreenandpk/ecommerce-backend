from django.urls import path
from apps.orders.views.admin_views import (
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderStatsView,
    AdminOrderUpdateView,
)

urlpatterns = [
    path("admin/orders/", AdminOrderListView.as_view()),
    path("admin/orders/<int:id>/", AdminOrderDetailView.as_view()),
    path("admin/orders/<int:id>/update/", AdminOrderUpdateView.as_view()),
    path("admin/orders/stats/", AdminOrderStatsView.as_view()),
]
