from django.contrib import admin
from .models import Category, TruckModel, Part, Inquiry, Engine, PartImage, CartItem, Order, OrderItem
from django.db import models

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
    search_fields = ('name',)

class PartImageInline(admin.TabularInline):  # or admin.StackedInline
    model = PartImage
    extra = 1


@admin.register(TruckModel)
class TruckModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'manufacturer', 'year_range', 'has_image', 'has_image_url')
    search_fields = ('name', 'manufacturer')
    fields = ('name', 'slug', 'manufacturer', 'year_range', 'description', 'image', 'image_url')
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def has_image_url(self, obj):
        return bool(obj.image_url)
    has_image_url.boolean = True
    has_image_url.short_description = 'Has Image URL'
  

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('part_number', 'name')}
    list_display = ('name', 'part_number', 'category', 'price', 'stock', 'has_image', 'is_active')
    list_filter = ('is_active', 'category', 'truck_models')
    list_editable = ('is_active', 'stock')
    search_fields = ('name', 'part_number')
    filter_horizontal = ('truck_models',)
    inlines = [PartImageInline]
    
    def has_image(self, obj):
        return bool(obj.image or obj.image_url)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'part_number', 'slug', 'description', 'category')
        }),
        ('Images', {
            'fields': ('image', 'image_url'),
            'description': 'You can either upload an image directly or provide an external URL to an image.'
        }),
        ('Inventory', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Related', {
            'fields': ('truck_models',)
        }),
    )


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'part_number', 'submitted_at', 'is_resolved')
    list_filter = ('is_resolved', 'submitted_at')
    search_fields = ('customer_name', 'customer_email', 'part_number')
    date_hierarchy = 'submitted_at'
    readonly_fields = ('submitted_at',)

@admin.register(Engine)
class EngineAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_truck_models', 'power_output', 'fuel_type', 'emissions_standard')
    search_fields = ('name', 'truck_models__name')
    list_filter = ('fuel_type', 'emissions_standard', 'power_output')
    filter_horizontal = ('truck_models',) 

    def get_truck_models(self, obj):
        return ", ".join([tm.name for tm in obj.truck_models.all()])
    get_truck_models.short_description = 'Truck Models'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'customer_email', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'country')
    search_fields = ('order_id', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'city', 'postal_code', 'country')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'part', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('session_key', 'part__name', 'part__part_number')

