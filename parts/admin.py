from django.contrib import admin
from .models import Category, TruckModel, Part, Inquiry, Engine, PartImage, CartItem, Order, OrderItem
from django.db import models
from django import forms
from .widgets import CloudinaryMediaLibraryWidget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')
    search_fields = ('name',)


# Widget that allows multiple selection, but form expects a single file
class MultipleImageWidget(forms.ClearableFileInput):
    allow_multiple_selected = True
    def __init__(self, attrs=None):
        final_attrs = {'multiple': True}
        if attrs:
            final_attrs.update(attrs)
        super().__init__(final_attrs)

class PartImageForm(forms.ModelForm):
    class Meta:
        model = PartImage
        fields = ('image', 'image_url')
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*', 'class': 'multiple-image-input'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = "You can select multiple images at once by holding Ctrl/Cmd while clicking. Each file will be added as a separate thumbnail."

class PartImageInline(admin.TabularInline):
    model = PartImage
    form = PartImageForm
    extra = 1
    fields = ('image', 'image_url')
    readonly_fields = ()
    
    def get_formset(self, request, obj=None, **kwargs):
        """Override to handle multiple file uploads"""
        FormSet = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(FormSet):
            def full_clean(self):
                """Override to handle multiple files from a single input"""
                super().full_clean()
                
                # Look for forms with multiple files selected
                for form in self.forms:
                    if hasattr(form, 'cleaned_data') and 'image' in form.cleaned_data:
                        files = form.cleaned_data['image']
                        if isinstance(files, list) and len(files) > 1:
                            # Create additional forms for extra files
                            for extra_file in files[1:]:
                                # Create a new form data dict
                                new_form_data = form.cleaned_data.copy()
                                new_form_data['image'] = extra_file
                                
                                # Add to the formset
                                self.forms.append(self._construct_form(len(self.forms), **{
                                    'data': new_form_data,
                                    'instance': None
                                }))
        
        return CustomFormSet
    
    class Media:
        js = ('admin/js/multiple_image_handler.js',)
        css = {
            'all': ('admin/css/multiple_image_admin.css',)
        }


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
        ('Main Image', {
            'fields': ('image', 'image_url'),
            'description': 'Upload the main image here. It will automatically be added to thumbnail images below.'
        }),
        ('Inventory', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Related', {
            'fields': ('truck_models',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to automatically add main image to thumbnails"""
        # Check if this is an existing object and if the main image has changed
        old_image = None
        old_image_url = None
        
        if change and obj.pk:
            # Get the old values
            old_obj = Part.objects.get(pk=obj.pk)
            old_image = old_obj.image
            old_image_url = old_obj.image_url
        
        # Save the main object first
        super().save_model(request, obj, form, change)
        
        # Check if main image was added or changed
        image_changed = False
        new_image_value = None
        new_image_url_value = None
        
        # Check if image field changed
        if obj.image and (not old_image or str(obj.image) != str(old_image)):
            image_changed = True
            new_image_value = obj.image
        
        # Check if image_url field changed  
        if obj.image_url and obj.image_url != old_image_url:
            image_changed = True
            new_image_url_value = obj.image_url
        
        # If main image changed, add it to thumbnails automatically
        if image_changed:
            # Create a new PartImage entry
            if new_image_value:
                # Check if this image doesn't already exist in thumbnails
                if not PartImage.objects.filter(part=obj, image=new_image_value).exists():
                    PartImage.objects.create(part=obj, image=new_image_value)
            
            if new_image_url_value:
                # Check if this URL doesn't already exist in thumbnails
                if not PartImage.objects.filter(part=obj, image_url=new_image_url_value).exists():
                    PartImage.objects.create(part=obj, image_url=new_image_url_value)
    
    def save_related(self, request, form, formsets, change):
        """Override to handle multiple image uploads and auto-add main image"""
        super().save_related(request, form, formsets, change)
        
        # Handle multiple file uploads from the PartImage inline
        for formset in formsets:
            if formset.model == PartImage:
                for inline_form in formset.forms:
                    if inline_form.cleaned_data and not inline_form.cleaned_data.get('DELETE', False):
                        files = inline_form.cleaned_data.get('image')
                        if files and isinstance(files, list):
                            # Handle multiple files
                            part_instance = form.instance
                            image_url = inline_form.cleaned_data.get('image_url')
                            
                            for i, file in enumerate(files):
                                if i == 0:
                                    # First file - use the existing form
                                    if inline_form.instance.pk:
                                        inline_form.instance.image = file
                                        inline_form.instance.save()
                                    else:
                                        PartImage.objects.create(
                                            part=part_instance,
                                            image=file,
                                            image_url=image_url if i == 0 else None
                                        )
                                else:
                                    # Additional files - create new PartImage instances
                                    PartImage.objects.create(
                                        part=part_instance,
                                        image=file
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

