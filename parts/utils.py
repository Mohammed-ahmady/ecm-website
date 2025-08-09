"""
Utility functions and classes for the parts app.
"""
from decimal import Decimal
from .models import CartItem


class ModernCart:
    """Modern cart class with database persistence"""
    
    def __init__(self, request):
        self.session = request.session
        
        # Ensure we have a valid session key
        if not request.session.session_key:
            request.session.create()
            
        self.session_key = request.session.session_key
        
        # Set a longer session expiry for the cart (2 weeks)
        request.session.set_expiry(60*60*24*14)  # 14 days in seconds
        
        # Mark session as modified to ensure it gets saved
        request.session.modified = True

    def add(self, part, quantity=1):
        """
        Add a part to the cart or increase its quantity
        
        Raises:
            ValueError: If the requested quantity exceeds available stock
        """
        # Check if we have enough stock
        if part.stock < quantity:
            raise ValueError(f"Sorry, only {part.stock} units of {part.name} are available.")
            
        # Get or create the cart item
        cart_item, created = CartItem.objects.get_or_create(
            session_key=self.session_key,
            part=part,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # If updating existing item, check if new total exceeds stock
            new_quantity = cart_item.quantity + quantity
            if part.stock < new_quantity:
                raise ValueError(f"Sorry, adding {quantity} more would exceed the available stock of {part.stock}.")
                
            cart_item.quantity = new_quantity
            cart_item.save()
            
        return cart_item

    def update(self, part, quantity):
        """
        Update the quantity of a part in the cart
        
        Raises:
            ValueError: If the requested quantity exceeds available stock
        """
        try:
            cart_item = CartItem.objects.get(session_key=self.session_key, part=part)
            
            if quantity > 0:
                # Check if we have enough stock for the requested quantity
                if part.stock < quantity:
                    raise ValueError(f"Sorry, only {part.stock} units of {part.name} are available.")
                    
                cart_item.quantity = quantity
                cart_item.save()
                return cart_item
            else:
                # Remove item if quantity is 0
                cart_item.delete()
                return None
        except CartItem.DoesNotExist:
            return None

    def remove(self, part):
        """Remove a part from the cart"""
        CartItem.objects.filter(session_key=self.session_key, part=part).delete()

    def get_items(self):
        """Get all items in the cart with optimized database queries"""
        return CartItem.objects.filter(session_key=self.session_key).select_related('part', 'part__category').prefetch_related('part__truck_models')

    def get_total_price(self):
        """Calculate total price of all items in cart"""
        items = self.get_items()
        return sum(item.total_price for item in items)

    def get_total_items(self):
        """Get total number of items in cart"""
        items = self.get_items()
        return sum(item.quantity for item in items)

    def clear(self):
        """Clear all items from the cart"""
        CartItem.objects.filter(session_key=self.session_key).delete()


def get_cart_response_data(cart, updated_item=None):
    """Generate standardized cart response data for AJAX requests"""
    # Calculate the cart totals
    total_items = cart.get_total_items()
    total_price = float(cart.get_total_price())
    
    data = {
        'success': True,
        'cart_total_items': total_items,
        'cart_total_price': total_price,
        'total_items': total_items,
        'cart_total': total_price,
    }
    
    # Add specific item data if provided
    if updated_item:
        item_total = float(updated_item.total_price) if updated_item.part.price else 0
        data.update({
            'part_id': updated_item.part.id,
            'quantity': updated_item.quantity,
            'item_total': item_total
        })
    
    return data


def is_ajax_request(request):
    """Check if the request is an AJAX request"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def get_search_queryset(queryset, query_params):
    """Apply search filters to a queryset based on query parameters"""
    from django.db.models import Q
    
    query = query_params.get('q')
    category_slug = query_params.get('category')
    truck_model_slug = query_params.get('truck_model')
    
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(part_number__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(truck_models__name__icontains=query)
        ).distinct()

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if truck_model_slug:
        queryset = queryset.filter(truck_models__slug=truck_model_slug)

    return queryset
