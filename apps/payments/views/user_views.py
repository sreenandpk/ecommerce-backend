import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from apps.orders.models import Order
from ..models import Payment
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.is_paid:
            return Response({"detail": "Order already paid"}, status=400)
        payment, _ = Payment.objects.get_or_create(
            user=request.user,
            order=order,
            defaults={
                "amount": order.total_amount,
                "currency": "INR",
            }
        )
        razorpay_order = razorpay_client.order.create({
            "amount": int(order.total_amount * 100),
            "currency": "INR",
            "payment_capture": 1,
        })
        payment.razorpay_order_id = razorpay_order["id"]
        payment.save()
        return Response({
            "payment_id": payment.id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key": settings.RAZORPAY_KEY_ID,
        })
class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        data = request.data
        payment = get_object_or_404(
            Payment,
            razorpay_order_id=data.get("razorpay_order_id"),
            user=request.user
        )
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"],
            })
        except razorpay.errors.SignatureVerificationError:
            payment.status = "failed"
            payment.save()
            return Response({"detail": "Payment verification failed"}, status=400)
        payment.razorpay_payment_id = data["razorpay_payment_id"]
        payment.razorpay_signature = data["razorpay_signature"]
        payment.status = "success"
        payment.save()
        order = payment.order
        order.is_paid = True
        order.status = "pending"  # ✅ UPDATED: Move from awaiting_payment to pending
        order.payment_id = payment.razorpay_payment_id
        order.save()
        return Response({"detail": "Payment successful"})
class RazorpayConfigView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "key_id": settings.RAZORPAY_KEY_ID
        })