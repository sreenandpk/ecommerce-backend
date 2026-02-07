from .user_urls import urlpatterns as user_urls
from .admin_urls import urlpatterns as admin_urls

urlpatterns = user_urls + admin_urls
