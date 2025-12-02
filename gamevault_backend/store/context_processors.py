"""
Context processors for the store app.
Makes certain data available to all templates.
"""
from .models import Cart

def cart_count(request):
    """
    Add cart item count to template context for all pages.
    Shows badge on cart icon in navigation.
    """
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, status='active')
            count = cart.items.count()
            return {'cart_count': count}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}
