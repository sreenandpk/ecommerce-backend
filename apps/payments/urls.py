# apps/payments/urls.py
from django.urls import path
from apps.payments.views.user_views import (
    CreateRazorpayOrderView,
    VerifyRazorpayPaymentView,
    RazorpayConfigView,
)
urlpatterns = [
    path(
        "payments/razorpay/create/<int:order_id>/",
        CreateRazorpayOrderView.as_view(),
        name="razorpay-create",
    ),
    path(
        "payments/razorpay/verify/",
        VerifyRazorpayPaymentView.as_view(),
        name="razorpay-verify",
    ),
    path(
        "payments/razorpay/config/",
        RazorpayConfigView.as_view(),
        name="razorpay-config",
    ),
]
