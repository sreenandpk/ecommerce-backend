from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from apps.accounts.models import User
from apps.accounts.serializers import AdminUserSerializer
from apps.orders.models import Order
from rest_framework.pagination import PageNumberPagination
class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        try:
            queryset = User.objects.all().order_by("-created_at")
            paginator=PageNumberPagination()
            page=paginator.paginate_queryset(queryset,request)
            serializer = AdminUserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception:
            return Response(
                {"detail": "Failed to load users"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class AdminUserDetailView(APIView):
    permission_classes=[IsAuthenticated,IsAdminUser]
    def get(self,request,pk):
        try:
            user=User.objects.get(pk=pk)
            serializer=AdminUserSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail":"user not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"detail":"failed to load user"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def patch(self,request,pk):
        try:
            user=User.objects.get(pk=pk)
            if request.user.id==user.id and "is_staff" in request.data:
                return Response({"detail":"you cannot change your own admin status"},status=status.HTTP_400_BAD_REQUEST)
            serializer=AdminUserSerializer(user,data=request.data,partial=True)
            if not serializer.is_valid():
                return Response(
                    {"errors":serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                serializer.data,status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"detail":"user not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"detail":"failed to update user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminUserBlockView(APIView):
    permission_classes=[IsAuthenticated,IsAdminUser]
    def patch(self,request,pk):
        try:
            user=User.objects.get(pk=pk)
            if request.user.id==user.id:
                return Response(
                    {"detail":"you cannot block your own account"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.is_active: # Suggesting a block action
                # 1. PERMISSION CHECK
                # Prevent blocking superusers (no one should block a superuser via this simple API)
                if user.is_superuser:
                    return Response(
                        {"detail": "You cannot block a Superuser."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Prevent blocking ANY admin/staff member
                if user.is_staff:
                    return Response(
                        {"detail": "You cannot block an admin account."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 2. PENDING ORDERS CHECK
                # Check for ANY pending orders, regardless of payment status (e.g. COD)
                has_pending_orders = Order.objects.filter(
                    user=user, 
                    status="pending"
                ).exists()
                
                if has_pending_orders:
                    return Response(
                        {"detail": "Cannot block user with pending orders. Please process or cancel their orders first."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            user.is_active= not user.is_active
            user.save()
            return Response({
                "id":user.id,
                "email":user.email,
                "is_active":user.is_active,
                "message":"User Unblocked" if user.is_active else "User Blocked"
            },
            status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"detail":"User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"detail":"failed to update user status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
