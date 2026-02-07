from rest_framework import serializers
from .models import Review
class ReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_image = serializers.ImageField(source="user.image", read_only=True)
    class Meta:
        model = Review
        fields = [
            "id",
            "user_id",
            "user_name",
            "user_image",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "user_name",
            "created_at",
            "updated_at",
        ]
