from django.contrib import admin
from .models import Category, TruckModel, Part, Inquiry

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
    search_fields = ('name',)

@admin.register(TruckModel)
class TruckModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'manufacturer', 'year_range')
    search_fields = ('name', 'manufacturer')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('part_number', 'name')}
    list_display = ('name', 'part_number', 'category', 'price', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'category', 'truck_models')
    list_editable = ('is_active', 'stock_quantity')
    search_fields = ('name', 'part_number')
    filter_horizontal = ('truck_models',)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'part_number', 'submitted_at', 'is_resolved')
    list_filter = ('is_resolved', 'submitted_at')
    search_fields = ('customer_name', 'customer_email', 'part_number')
    date_hierarchy = 'submitted_at'
    readonly_fields = ('submitted_at',)