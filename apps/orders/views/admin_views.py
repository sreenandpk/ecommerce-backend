from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import models
from django.db.models import Sum

from ..models import Order, OrderItem
from ..serializers.admin_serializers import AdminOrderSerializer


# =======================
# ADMIN – ORDER LIST
# =======================
class AdminOrderListView(ListAPIView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]


# =======================
# ADMIN – ORDER DETAIL
# =======================
class AdminOrderDetailView(RetrieveAPIView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product")
    )
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"


# =======================
# ADMIN – ORDER UPDATE
# (STATUS / PAYMENT)
# =======================
class AdminOrderUpdateView(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        order = self.get_object()

        new_status = request.data.get("status")
        new_paid = request.data.get("is_paid")

        allowed_status = [
            "pending",
            "shipped",
            "delivered",
            "cancelled",
            "paid",
        ]

        # ❌ block changes after final states
        if order.status in ["delivered", "cancelled"]:
            return Response(
                {"detail": f"Order is already {order.status} and cannot be modified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ STATUS UPDATE VALIDATION (State Machine)
        if new_status:
            if new_status not in allowed_status:
                return Response(
                    {"detail": f"Invalid status: {new_status}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Define valid transitions
            valid_next_states = {
                "pending": ["shipped", "delivered", "cancelled"],
                "shipped": ["delivered", "cancelled"],
                "paid": ["shipped", "delivered", "cancelled"],
            }

            if new_status != order.status: # Only validate if status is actually changing
                if order.status in valid_next_states:
                    if new_status not in valid_next_states[order.status]:
                        return Response(
                            {"detail": f"Cannot transition from {order.status} to {new_status}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                order.status = new_status

            # cancel ⇒ unpaid (keep existing logic)
            if new_status == "cancelled":
                order.is_paid = False

            # ✅ Set shipped_at logic
            if new_status == "shipped" and not order.shipped_at:
                from django.utils import timezone
                order.shipped_at = timezone.now()

        # ✅ PAYMENT UPDATE (OPTIONAL)
        if new_paid is not None:
            order.is_paid = bool(new_paid)

        order.save()

        return Response(
            AdminOrderSerializer(order).data,
            status=status.HTTP_200_OK,
        )


# =======================
# ADMIN – DASHBOARD STATS
# =======================
class AdminOrderStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_orders = Order.objects.count()
        paid_orders = Order.objects.filter(is_paid=True).count()

        total_revenue = (
            Order.objects
            .filter(is_paid=True)
            .aggregate(total=Sum("total_amount"))["total"]
            or 0
        )

        total_products_sold = (
            OrderItem.objects
            .aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        # Graph Data (Last 7 Days)
        from django.utils import timezone
        from django.db.models.functions import TruncDate
        
        last_7_days = timezone.now().date() - timezone.timedelta(days=6)
        
        daily_stats = (
            Order.objects
            .filter(is_paid=True, created_at__date__gte=last_7_days)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                orders=models.Count('id'),
                revenue=Sum('total_amount')
            )
            .order_by('date')
        )

        # Format for frontend
        graph_data = []
        stats_dict = {str(stat['date']): stat for stat in daily_stats}
        
        for i in range(7):
            date_obj = last_7_days + timezone.timedelta(days=i)
            date_str = str(date_obj)
            day_name = date_obj.strftime("%a") # Mon, Tue...
            
            if date_str in stats_dict:
                entry = stats_dict[date_str]
                graph_data.append({
                    "name": day_name,
                    "orders": entry['orders'],
                    "revenue": float(entry['revenue'] or 0)
                })
            else:
                graph_data.append({
                    "name": day_name,
                    "orders": 0,
                    "revenue": 0
                })

        return Response({
            "total_orders": total_orders,
            "paid_orders": paid_orders,
            "total_products_sold": total_products_sold,
            "total_revenue": total_revenue,
            "graph_data": graph_data
        })
