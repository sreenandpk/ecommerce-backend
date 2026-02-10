from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("id", "email", "name", "password")

    def validate_email(self, value):
        if not value.lower().endswith("@gmail.com"):
            raise serializers.ValidationError("Only @gmail.com email addresses are permitted")
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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Check if user exists and password is correct first
        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            existing_user = None

        if existing_user and existing_user.check_password(password):
            if not existing_user.is_active:
                 raise serializers.ValidationError(
                    {"detail": "User account is disabled"}
                )

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password"}
            )

        # Double check (redundant but safe)
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "User account is disabled"}
            )

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    from apps.products.serializers.user_serializers import ProductSerializer
    from apps.products.models import Product
    recently_viewed = ProductSerializer(many=True, read_only=True)
    recently_viewed_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Product.objects.all(), source='recently_viewed'
    )

    class Meta:
        model = User
        fields = ("id", "email", "name", "image", "created_at", "is_staff", "recently_viewed", "recently_viewed_ids")
        read_only_fields = ("id", "created_at", "is_staff")

    def validate_email(self, value):
        request = self.context.get("request")
        user = request.user if request else None

        if user and User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

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
        read_only_fields = (
            "id",
            "created_at",
        )