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
        # 0. Clean input (very important for AWS/Postgres issues)
        email_in = attrs.get("email", "").strip()
        email = email_in.lower()
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError({"detail": "Email and password are required"})

        # 1. Try standard Django authentication
        user = authenticate(username=email, password=password)
        
        # 2. Manual fallback with VERY verbose error reporting for debugging
        if not user:
            try:
                # Try finding the user exactly as entered first
                existing_user = User.objects.filter(email=email_in).first()
                if not existing_user:
                    # Try finding case-insensitive
                    existing_user = User.objects.filter(email__iexact=email).first()
                
                if existing_user:
                    if not existing_user.check_password(password):
                        # WRONG PASSWORD
                        raise serializers.ValidationError({"detail": "Authentication failed: Password mismatch."})
                    if not existing_user.is_active:
                        # INACTIVE
                        raise serializers.ValidationError({"detail": "Authentication failed: User account is disabled."})
                    
                    # If we reached here, password is GOOD and user is ACTIVE, but authenticate() still failed
                    user = existing_user
                else:
                    # USER NOT FOUND
                    raise serializers.ValidationError({"detail": f"Authentication failed: User with email '{email_in}' not found."})
            
            except Exception as e:
                # Catch any DB errors (like MultipleObjectsReturned)
                raise serializers.ValidationError({"detail": f"Authentication Error: {str(e)}"})
                
        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    from apps.products.serializers.user_serializers import ProductSerializer
    from apps.products.models import Product
    
    recently_viewed = serializers.SerializerMethodField()
    recently_viewed_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Product.objects.all(), source='recently_viewed'
    )

    class Meta:
        model = User
        fields = ("id", "email", "name", "image", "created_at", "is_staff", "recently_viewed", "recently_viewed_ids")
        read_only_fields = ("id", "created_at", "is_staff")

    def get_recently_viewed(self, obj):
        from apps.products.serializers.user_serializers import ProductSerializer
        # Filter only active products to avoid serialization errors with soft-deleted or inactive items
        items = obj.recently_viewed.filter(is_active=True)
        return ProductSerializer(items, many=True, context=self.context).data

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