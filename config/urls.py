from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ ACCOUNTS (FIXED)
    path("api/accounts/", include("apps.accounts.urls")),

   # PRODUCTS (USER)
    path("api/", include("apps.products.urls.user_urls")),

    # PRODUCTS (ADMIN)
    path("api/", include("apps.products.urls.admin_urls")),

    # cart
    path("api/", include("apps.cart.urls")),

    # wishlist
    path("api/", include("apps.wishlist.urls")),

    # orders
    path("api/", include("apps.orders.urls.user_urls")),
    path("api/", include("apps.orders.urls.admin_urls")),

    # payments
    path("api/", include("apps.payments.urls")),

    # reviews
    path("api/", include("apps.reviews.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
