from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Part, Category, TruckModel, Inquiry, CartItem, Order, OrderItem
from .forms import InquiryForm
from .utils import ModernCart, get_cart_response_data, is_ajax_request, get_search_queryset

@require_POST
def add_to_cart(request, part_id):
    """
    Add a part to the shopping cart.
    
    Handles both AJAX and form submissions. Increases quantity if part already exists in cart.
    
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


def cart_detail(request):
    """
    Display the shopping cart with all items and totals.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered cart detail template with cart items and totals
    """
    cart = ModernCart(request)
    cart_items = cart.get_items()
    total_price = cart.get_total_price()
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': cart.get_total_items(),
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
    cart = ModernCart(request)
    cart_items = cart.get_items()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('parts:part_list')
    
    total_price = cart.get_total_price()
    
    if request.method == 'POST':
        try:
            order = Order.objects.create(
                customer_name=request.POST['customer_name'],
                customer_email=request.POST['customer_email'],
                customer_phone=request.POST['customer_phone'],
                shipping_address=request.POST['shipping_address'],
                city=request.POST['city'],
                postal_code=request.POST.get('postal_code', ''),
                country=request.POST.get('country', 'Egypt'),
                total_amount=total_price,
                notes=request.POST.get('notes', '')
            )
            
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    part=cart_item.part,
                    quantity=cart_item.quantity,
                    price=cart_item.part.price or 0
                )
            
            cart.clear()
            
            messages.success(request, f'Order #{order.order_id} placed successfully! We will contact you soon.')
            return render(request, 'cart/order_success.html', {'order': order})
            
        except Exception as e:
            messages.error(request, 'There was an error processing your order. Please try again.')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': cart.get_total_items(),
    }
    return render(request, 'cart/checkout.html', context)


class PartListView(ListView):
    """View for listing parts with search and filters"""
    model = Part
    template_name = 'parts/part_list.html'
    context_object_name = 'parts'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
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
        return super().get_queryset().filter(is_active=True)


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