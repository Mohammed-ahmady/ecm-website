import os
from django.db import models
from django.utils.text import slugify 
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from cloudinary.models import CloudinaryField

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
    image = CloudinaryField('image', folder='ecm_website_media/truck_models', blank=True, null=True, help_text="Image of the truck model")
    image_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Alternative external image URL if you don't want to upload an image directly")
    description = models.TextField(blank=True, null=True, help_text="Brief description of the truck model")

    class Meta:
        verbose_name = "Truck Model"
        verbose_name_plural = "Truck Models"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.manufacturer} {self.name}"
        
    def get_image_url(self):
        """Return the image URL, preferring image_url if provided, otherwise using the Cloudinary image"""
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        return None

class Engine(models.Model):
    name = models.CharField(max_length=100)
    power_output = models.CharField(max_length=50, blank=True, null=True)  # e.g., "250 HP"
    fuel_type = models.CharField(max_length=50, blank=True, null=True)     # e.g., "Diesel"
    emissions_standard = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Euro 6"
    truck_models = models.ManyToManyField(TruckModel, related_name='engines')  # updated field for having n:n engines per truck model
    
    def __str__(self):
        if self.pk:
            truck_names = ", ".join([truck.name for truck in self.truck_models.all()])
            return f"{self.name} (Used in: {truck_names})"
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    part_number = models.CharField(max_length=100, unique=True, db_index=True, help_text="Unique identifier for the part")
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='parts')
    truck_models = models.ManyToManyField(TruckModel, blank=True, related_name='parts')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price in EGP")
    image = CloudinaryField('image', folder='ecm_website_media/parts_images', blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Alternative external image URL if you don't want to upload an image directly")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Designates whether this part should be available on the website.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True) # Add slug for cleaner URLs
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
        ]

    def save(self, *args, **kwargs):
        # Store the old image URL if it exists
        old_image_url = None
        if self.pk:
            old_part = Part.objects.get(pk=self.pk)
            old_image_url = old_part.image_url

        # Save the model first
        if not self.slug:
            self.slug = slugify(f"{self.part_number}-{self.name}")
        super().save(*args, **kwargs)
        
        # After saving, check if image_url was added or changed
        if self.image_url and self.image_url != old_image_url:
            # Check if this URL already exists in the part's images
            if not PartImage.objects.filter(part=self).exists() or not any(pi.image.url == self.image_url for pi in self.images.all()):
                # Create a new PartImage with the same URL
                from cloudinary.uploader import upload
                from cloudinary.utils import cloudinary_url
                
                # If it's a direct URL to an image, we'll create a PartImage that references it
                try:
                    # First, check if this is already a Cloudinary URL
                    if 'cloudinary.com' in self.image_url:
                        # Extract the public ID if it's a Cloudinary URL
                        from urllib.parse import urlparse
                        parsed_url = urlparse(self.image_url)
                        path_parts = parsed_url.path.strip('/').split('/')
                        if 'upload' in path_parts:
                            upload_index = path_parts.index('upload')
                            if upload_index < len(path_parts) - 1:
                                # The public ID is everything after 'upload'
                                public_id = '/'.join(path_parts[upload_index+1:])
                                # Create a new PartImage with the same URL
                                PartImage.objects.create(part=self, image=public_id)
                    else:
                        # For non-Cloudinary URLs, we'd need to implement a different approach
                        # This would typically involve downloading and re-uploading to Cloudinary
                        # For now, we'll just create a placeholder for demonstration
                        # In a production environment, you'd want to properly upload the image
                        pass
                except Exception as e:
                    # Log the error but don't prevent saving
                    print(f"Error creating PartImage from URL: {e}")

    def __str__(self):
        return f"{self.name} ({self.part_number})"
    
    def get_image_url(self):
        """
        Returns the best available image URL for this part.
        First checks for an external URL, then falls back to the uploaded image.
        """
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        return None


def part_image_upload_to(instance, filename):
    # Get the part name or slug
    part_slug = slugify(instance.part.name)
    # Build the path: "parts_images/<part-name>/<original_filename>"
    return os.path.join('parts_images', part_slug, filename)


class PartImage(models.Model):
    part = models.ForeignKey(Part, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image', folder='ecm_website_media/parts_images')
    image_url = models.URLField(max_length=1000, blank=True, null=True, help_text="External image URL")
    
    def __str__(self):
        return f"Image for {self.part.name}"
    
    def get_image_url(self):
        """Returns the best available image URL for this part image."""
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        return None


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


class CartItem(models.Model):
    """Database-backed cart item for better persistence"""
    session_key = models.CharField(max_length=40, db_index=True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        unique_together = ('session_key', 'part')
        indexes = [
            models.Index(fields=['session_key', 'added_at']),
        ]
    
    def __str__(self):
        return f"{self.part.name} (x{self.quantity})"
    
    @property
    def total_price(self):
        return self.part.price * self.quantity if self.part.price else 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Egypt')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, help_text="Special instructions or notes")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.part.name} (x{self.quantity}) - Order {self.order.order_id}"
    
    @property
    def total_price(self):
        return self.price * self.quantity