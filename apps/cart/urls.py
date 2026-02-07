from rest_framework.routers import DefaultRouter
from apps.cart.views.user_views import CartItemViewSet

router = DefaultRouter()
router.register(r"cart", CartItemViewSet, basename="cart")

urlpatterns = router.urls
