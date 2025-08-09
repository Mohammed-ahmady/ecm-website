from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django_ratelimit.decorators import ratelimit
import json
import logging

from .models import Part, Category, TruckModel, Inquiry, CartItem, Order, OrderItem
from .forms import InquiryForm
from .utils import ModernCart, get_cart_response_data, is_ajax_request, get_search_queryset

# Set up logger for this module
logger = logging.getLogger('parts')

@require_POST
@ratelimit(key='ip', rate='10/m', method=['POST'], block=True)
def add_to_cart(request, part_id):
    """
    Add a part to the shopping cart.
    
    Handles both AJAX and form submissions. Increases quantity if part already exists in cart.
    Rate limited to 10 requests per minute per IP to prevent abuse.
    
    Args:
        request: HTTP request object
        part_id: ID of the part to add to cart
        
    Returns:
        JsonResponse for AJAX requests or redirect for form submissions
    """
    cart = ModernCart(request)
    part = get_object_or_404(Part, id=part_id)
    
    if request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart_item = cart.add(part=part, quantity=quantity)
        
        if is_ajax_request(request):
            cart_count = CartItem.objects.filter(session_key=request.session.session_key).count()
            return JsonResponse({
                'success': True,
                'message': f'{part.name} added to cart!',
                'cart_count': cart_count,
                'cart_total_items': cart.get_total_items(),
                'cart_total_price': float(cart.get_total_price()),
                'item_total_price': float(cart_item.total_price)
            })
        
        messages.success(request, f'{part.name} added to cart!')
        return redirect('parts:cart_detail')
    
    except ValueError as e:
        if is_ajax_request(request):
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        messages.error(request, str(e))
        return redirect('parts:part_detail', slug=part.slug)


def cart_detail(request):
    """
    Display the shopping cart with all items and totals.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered cart detail template with cart items and totals
    """
    cart = ModernCart(request)
    # Optimize query with select_related to avoid N+1 problem
    cart_items = CartItem.objects.filter(session_key=request.session.session_key).select_related('part', 'part__category')
    
    # Calculate total price once to avoid multiple calculations
    total_price = sum(item.total_price for item in cart_items)
    
    # Get selected payment method from session
    selected_payment_method = request.session.get('selected_payment_method', 'cod')
    payment_methods = {
        'cod': 'Cash on Delivery (COD)',
        'bank_transfer': 'Bank Transfer',
        'installments': 'Installments',
        'mobile_wallet': 'Mobile Wallets (Vodafone Cash, etc.)'
    }
    payment_method_display = payment_methods.get(selected_payment_method, 'Cash on Delivery (COD)')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': cart.get_total_items(),
        'selected_payment_method': selected_payment_method,
        'payment_method_display': payment_method_display,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def update_cart(request, part_id):
    """
    Update the quantity of a part in the cart.
    
    Args:
        request: HTTP request object
        part_id: ID of the part to update in cart
        
    Returns:
        JsonResponse for AJAX requests or redirect for form submissions
    """
    cart = ModernCart(request)
    part = get_object_or_404(Part, id=part_id)
    
    try:
        # Get quantity from POST data
        quantity = int(request.POST.get('quantity', 0))
        
        # Update the cart item and get the updated item
        cart_item = cart.update(part, quantity)
        
        if is_ajax_request(request):
            if cart_item:
                # Item was updated
                return JsonResponse({
                    'success': True,
                    'part_id': part_id,
                    'quantity': quantity,
                    'item_total': float(cart_item.total_price) if cart_item.part.price else 0,
                    'cart_total': float(cart.get_total_price()),
                    'total_items': cart.get_total_items()
                })
            else:
                # Item was removed (quantity was 0)
                return JsonResponse({
                    'success': True,
                    'cart_total': float(cart.get_total_price()),
                    'total_items': cart.get_total_items()
                })
        
        return redirect('parts:cart_detail')
    except Exception as e:
        if is_ajax_request(request):
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        messages.error(request, f"Error updating cart: {e}")
        return redirect('parts:cart_detail')


def remove_from_cart(request, part_id):
    """
    Remove a part completely from the shopping cart.
    
    Args:
        request: HTTP request object
        part_id: ID of the part to remove from cart
        
    Returns:
        JsonResponse for AJAX requests or redirect for form submissions
    """
    try:
        cart = ModernCart(request)
        part = get_object_or_404(Part, id=part_id)
        cart.remove(part)
        
        if is_ajax_request(request):
            return JsonResponse({
                'success': True,
                'part_id': part_id,
                'message': f'{part.name} removed from cart!',
                'cart_total': float(cart.get_total_price()),
                'total_items': cart.get_total_items()
            })
        
        messages.success(request, f'{part.name} removed from cart!')
        return redirect('parts:cart_detail')
    except Exception as e:
        if is_ajax_request(request):
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        messages.error(request, f"Error removing item: {e}")
        return redirect('parts:cart_detail')


@require_POST 
@ratelimit(key='ip', rate='20/m', method=['POST'], block=True)
def update_cart_quantity(request):
    """
    Update cart item quantity via AJAX.
    
    Expects JSON data with part_id and quantity.
    Rate limited to 20 requests per minute per IP.
    """
    try:
        data = json.loads(request.body)
        part_id = data.get('part_id')
        quantity = int(data.get('quantity', 1))
        
        # Use both cart systems to ensure consistency
        cart = ModernCart(request)
        part = get_object_or_404(Part, id=part_id)
        
        if quantity > 0:
            cart_item = cart.update(part, quantity)
            return JsonResponse({
                'success': True,
                'part_id': part_id,
                'quantity': quantity,
                'item_total': float(cart_item.total_price) if cart_item.part.price else 0,
                'cart_total': float(cart.get_total_price()),
                'total_items': cart.get_total_items()
            })
        else:
            # Remove item if quantity is 0
            cart.remove(part)
            return JsonResponse({
                'success': True,
                'part_id': part_id,
                'quantity': 0,
                'item_removed': True,
                'cart_total': float(cart.get_total_price()),
                'total_items': cart.get_total_items()
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST 
@ratelimit(key='ip', rate='10/m', method=['POST'], block=True)
def update_payment_method(request):
    """
    Update payment method selection via AJAX.
    
    Expects JSON data with payment_method.
    Rate limited to 10 requests per minute per IP.
    """
    try:
        data = json.loads(request.body)
        payment_method = data.get('payment_method', 'cod')
        
        # Store payment method in session
        request.session['selected_payment_method'] = payment_method
        
        # Get display text for the payment method
        payment_methods = {
            'cod': 'Cash on Delivery (COD)',
            'bank_transfer': 'Bank Transfer',
            'installments': 'Installments',
            'mobile_wallet': 'Mobile Wallets (Vodafone Cash, etc.)'
        }
        
        display_text = payment_methods.get(payment_method, 'Cash on Delivery (COD)')
        
        return JsonResponse({
            'success': True,
            'payment_method': payment_method,
            'display_text': display_text
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def checkout_page(request):
    """
    Handle the checkout process for placing orders.
    
    GET: Display checkout form with cart items
    POST: Process order creation and clear cart
    
    Args:
        request: HTTP request object
        
    Returns:
        Checkout form template or order success page
    """
    # Ensure we're using the same cart system throughout
    cart = ModernCart(request)
    cart_items = cart.get_items()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('parts:part_list')
    
    total_price = cart.get_total_price()
    
    # Get selected payment method from session
    selected_payment_method = request.session.get('selected_payment_method', 'cod')
    payment_methods = {
        'cod': 'Cash on Delivery (COD)',
        'bank_transfer': 'Bank Transfer',
        'installments': 'Installments',
        'mobile_wallet': 'Mobile Wallets (Vodafone Cash, etc.)'
    }
    payment_method_display = payment_methods.get(selected_payment_method, 'Cash on Delivery (COD)')
    
    if request.method == 'POST':
        try:
            logger.info(f"Starting checkout process for session: {request.session.session_key}")
            
            # Use database transaction to ensure all operations succeed or fail together
            with transaction.atomic():
                order = Order.objects.create(
                    customer_name=request.POST['customer_name'],
                    customer_email=request.POST['customer_email'],
                    customer_phone=request.POST['customer_phone'],
                    shipping_address=request.POST['shipping_address'],
                    city=request.POST['city'],
                    postal_code=request.POST.get('postal_code', ''),
                    country=request.POST.get('country', 'Egypt'),
                    total_amount=total_price,
                    notes=request.POST.get('notes', ''),
                    payment_method=selected_payment_method  # Store the selected payment method
                )
                
                logger.info(f"Created order #{order.order_id} for {order.customer_name}")
                
                for cart_item in cart_items:
                    # Validate stock availability before creating order item
                    if cart_item.part.stock < cart_item.quantity:
                        error_msg = f"Not enough stock for {cart_item.part.name}. Only {cart_item.part.stock} available."
                        logger.warning(f"Stock validation failed: {error_msg}")
                        raise ValueError(error_msg)
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        part=cart_item.part,
                        quantity=cart_item.quantity,
                        price=cart_item.part.price or 0
                    )
                    
                    # Update stock level
                    cart_item.part.stock -= cart_item.quantity
                    cart_item.part.save()
                    logger.info(f"Updated stock for part {cart_item.part.part_number}, new stock: {cart_item.part.stock}")
                
                # Clear the cart only if all operations succeed
                cart.clear()
                logger.info(f"Checkout completed successfully for order #{order.order_id}")
            
            messages.success(request, f'Order #{order.order_id} placed successfully! We will contact you soon.')
            return render(request, 'cart/order_success.html', {'order': order})
            
        except ValueError as e:
            logger.warning(f"Order validation error: {str(e)}")
            messages.error(request, str(e))
        except Exception as e:
            logger.exception(f"Unexpected error during checkout: {str(e)}")
            messages.error(request, 'There was an error processing your order. Please try again.')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': cart.get_total_items(),
        'selected_payment_method': selected_payment_method,
        'payment_method_display': payment_method_display,
    }
    return render(request, 'cart/checkout.html', context)


class PartListView(ListView):
    """View for listing parts with search and filters"""
    model = Part
    template_name = 'parts/part_list.html'
    context_object_name = 'parts'
    paginate_by = 12

    def get_queryset(self):
        # Use select_related for ForeignKey relationships and prefetch_related for M2M
        queryset = super().get_queryset().filter(is_active=True).select_related('category').prefetch_related('truck_models')
        return get_search_queryset(queryset, self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['truck_models'] = TruckModel.objects.all().order_by('name')
        context['current_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_truck_model'] = self.request.GET.get('truck_model', '')
        return context

class PartDetailView(DetailView):
    """View for a single part's details"""
    model = Part
    template_name = 'parts/part_detail.html'
    context_object_name = 'part'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).select_related('category').prefetch_related('truck_models', 'images')


class InquiryCreateView(CreateView):
    """View for the inquiry form"""
    model = Inquiry
    form_class = InquiryForm
    template_name = 'inquiry.html'
    success_url = reverse_lazy('inquiry')

    def form_valid(self, form):
        messages.success(self.request, "Your inquiry has been submitted successfully! We will get back to you shortly.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please correct the highlighted fields.")
        return super().form_invalid(form)


def home_view(request):
    """Function-based view for the home page"""
    truck_models = TruckModel.objects.all()
    return render(request, 'home.html', {
        'truck_models': truck_models,
    })