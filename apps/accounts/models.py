import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    username = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    image = models.ImageField(
        upload_to="profiles/",
        default="profiles/default.png",
    )
    recently_viewed = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="viewed_by"
    )
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = User.objects.get(pk=self.pk)
                if old.image and old.image != self.image:
                    if old.image.name != "profiles/default.png":
                        if os.path.isfile(old.image.path):
                            os.remove(old.image.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    def __str__(self):
        return self.email
