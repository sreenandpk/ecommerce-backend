from django.urls import path
from .views.auth_views import (
    RegisterView,
    LoginView,
    RefreshView,
    LogoutView,
)
from .views.user_views import (
    MeView,
    ProfileUpdateView,
)
from .views.admin_views import(
    AdminUserListView,
    AdminUserDetailView,
    AdminUserBlockView
)
urlpatterns = [
    # ---------- AUTH ----------
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # ---------- USER ----------
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    # ---------- ADMIN ----------
    path("admin/users/",AdminUserListView.as_view(),name="admin-users"),
    path("admin/users/<int:pk>/",AdminUserDetailView.as_view(),name="admin-user-detail"),
    path("admin/users/<int:pk>/block/",AdminUserBlockView.as_view(),name="admin-user-block"),
]
