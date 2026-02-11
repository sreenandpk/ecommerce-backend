from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for auth + /me
    """
    class Meta:
        model = User
        fields = ("id", "email", "name", "image", "is_staff", "is_superuser")
        read_only_fields = ("id", "is_staff", "is_superuser")


# =========================
# REGISTER
# =========================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("id", "email", "name", "password")

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")

        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            password=validated_data["password"],
        )
        return user


# =========================
# LOGIN
# =========================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError({"detail": "Email and password required"})

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        if not user_obj.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        if not user_obj.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled"})

        user = authenticate(username=email, password=password) or user_obj
        attrs["user"] = user
        return attrs


# =========================
# USER PROFILE
# =========================
class UserProfileSerializer(serializers.ModelSerializer):
    from apps.products.models import Product
    from apps.products.serializers.user_serializers import ProductSerializer

    recently_viewed = serializers.SerializerMethodField()
    recently_viewed_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Product.objects.all(),
        source="recently_viewed"
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "image",
            "created_at",
            "is_staff",
            "recently_viewed",
            "recently_viewed_ids",
        )
        read_only_fields = ("id", "created_at", "is_staff")

    def get_recently_viewed(self, obj):
        items = obj.recently_viewed.filter(is_active=True).order_by("-id")[:5]
        return self.ProductSerializer(
            items,
            many=True,
            context=self.context
        ).data


# =========================
# ADMIN
# =========================
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
