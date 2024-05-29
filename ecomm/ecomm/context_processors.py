from carts.models import Cart,CartItem
from carts.views import _cart_id
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.core.exceptions import ObjectDoesNotExist


def counter(request):
    cart_count = 0
    
    if 'admin' in request.path:
        return {}
    else:
        try:
            if request.user.is_authenticated:
                # If user is authenticated, get their cart items
                cart_items = CartItem.objects.filter(user=request.user, is_active=True)
                cart_count = cart_items.count()
            else:
                # For anonymous users, get cart items based on cart_id
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_count = CartItem.objects.filter(cart=cart, is_active=True).count()
        except Cart.DoesNotExist:
            cart_count = 0
    
    return {'cart_count': cart_count}



def cart_view(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        shipping_cost = 0
        if request.user.is_authenticated:
            # If user is authenticated, get their cart items
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('-created_at')
        else:
            # For anonymous users, get cart items based on cart_id
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at')

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (3 * total) / 100

        # Calculate shipping cost based on total
        if total > 100:
            shipping_cost = 0  # Free shipping
        elif total == 0:
            shipping_cost = 0  # No items, no shipping cost
        else:
            shipping_cost = 10

        grand_total = total + tax + shipping_cost
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax_base': tax,
        'shipping_cost_base': shipping_cost,
        'grand_total_base': grand_total,
    }
    return context


