from django.urls import path
from apps.orders.views.user_views import CreateOrderView, MyOrdersView, OrderDetailView
urlpatterns = [
    path("orders/create/", CreateOrderView.as_view(), name="order-create"),
    path("orders/", MyOrdersView.as_view(), name="my-orders"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),
]
