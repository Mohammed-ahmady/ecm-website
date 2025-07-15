from parts.models import CartItem

def cart_context(request):
    """Add cart item count to all templates"""
    if hasattr(request, 'session'):
        session_key = request.session.session_key
        if session_key:
            cart_count = CartItem.objects.filter(session_key=session_key).count()
        else:
            cart_count = 0
    else:
        cart_count = 0
    
    return {
        'cart_count': cart_count
    }
