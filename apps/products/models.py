from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )
    class Meta:
        ordering = ["name"]
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
class Allergen(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pincode = models.PositiveIntegerField(unique=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return f"{self.name} ({self.pincode})"
class Product(models.Model):
    CURRENCY_CHOICES = [
        ("INR", "Indian Rupee"),
        ("USD", "US Dollar"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="INR"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    image = models.ImageField(upload_to="products/")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="products"
    )
    allergens = models.ManyToManyField(
        Allergen,
        related_name="products",
        blank=True
    )
    description = models.TextField(blank=True)
    story = models.TextField(blank=True)
    average_rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    available_cities = models.ManyToManyField(
        City,
        related_name="products"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({self.price} {self.currency})"
class Nutrition(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="nutrition"
    )
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    fat = models.DecimalField(max_digits=6, decimal_places=2)
    carbs = models.DecimalField(max_digits=6, decimal_places=2)
    sugar = models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return f"{self.calories} kcal, {self.protein}g protein"
