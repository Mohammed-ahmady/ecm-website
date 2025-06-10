# C:\Users\Mohammed\Documents\ECM\parts\models.py

from django.db import models
from django.utils.text import slugify # For auto-generating slugs

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories" # Correct plural in admin

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TruckModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    manufacturer = models.CharField(max_length=100, default='Magirus') # Assuming Magirus for now
    year_range = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1980s, 2000-2010")

    class Meta:
        verbose_name = "Truck Model"
        verbose_name_plural = "Truck Models"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.manufacturer} {self.name}"

class Part(models.Model):
    name = models.CharField(max_length=255)
    part_number = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the part")
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='parts')
    truck_models = models.ManyToManyField(TruckModel, blank=True, related_name='parts')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price in EGP")
    stock_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='parts_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Designates whether this part should be available on the website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True) # Add slug for cleaner URLs
    stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.part_number}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.part_number})"

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, part, quantity=1, override_quantity=False):
        part_id = str(part.id)
        if part_id not in self.cart:
            self.cart[part_id] = {"quantity": 0, "price": str(part.price)}
        if override_quantity:
            self.cart[part_id]["quantity"] = quantity
        else:
            self.cart[part_id]["quantity"] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, part):
        part_id = str(part.id)
        if part_id in self.cart:
            del self.cart[part_id]
            self.save()

    def __iter__(self):
        from .models import Part
        part_ids = self.cart.keys()
        parts = Part.objects.filter(id__in=part_ids)
        for part in parts:
            cart_item = self.cart[str(part.id)]
            cart_item["part"] = part
            cart_item["total_price"] = float(cart_item["price"]) * cart_item["quantity"]
            yield cart_item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(float(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self):
        self.session["cart"] = {}
        self.save()


# New Inquiry Model
class Inquiry(models.Model):
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    part_number = models.CharField(max_length=100, blank=True, null=True, help_text="Optional: Specific part number inquired about")
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Inquiries"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Inquiry from {self.customer_name} ({self.customer_email})"