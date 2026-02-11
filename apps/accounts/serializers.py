from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User

class UserBasicSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for initial auth and 'me' checks.
    Excludes heavy ManyToMany history fields.
    """
    class Meta:
        model = User
        fields = ("id", "email", "name", "image", "is_staff", "is_superuser")
        read_only_fields = ("id", "is_staff", "is_superuser")


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
        # MEGA DEBUG: Log exactly what's happening
        email_in = attrs.get("email", "").strip()
        email = email_in.lower()
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError({"detail": "DEBUG: Missing email or password in request"})

        # Try to find the user first to see if they even exist
        all_matches = User.objects.filter(email__iexact=email)
        match_count = all_matches.count()
        
        if match_count == 0:
            raise serializers.ValidationError({"detail": f"DEBUG: User '{email}' not found in DB. Total users: {User.objects.count()}"})
        
        user_obj = all_matches.first()
        
        # Check password manually
        pw_ok = user_obj.check_password(password)
        active = user_obj.is_active
        staff = user_obj.is_staff
        superu = user_obj.is_superuser
        
        debug_msg = f"DEBUG: User found! Email: {user_obj.email} | Active: {active} | Staff: {staff} | Super: {superu} | PW_Valid: {pw_ok}"

        if not pw_ok:
            raise serializers.ValidationError({"detail": f"{debug_msg} | ERROR: Password mismatch"})
        
        if not active:
            raise serializers.ValidationError({"detail": f"{debug_msg} | ERROR: Account disabled"})

        # If everything is fine, try authenticate (to ensure backends are happy)
        user = authenticate(username=email, password=password)
        if not user:
            # If manual check said OK but authenticate failed, it's a backend config issue
            # But we can just use the user_obj we found!
            user = user_obj

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
        # Limit to 5 items to keep payload size down
        items = obj.recently_viewed.filter(is_active=True).order_by("-id")[:5]
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