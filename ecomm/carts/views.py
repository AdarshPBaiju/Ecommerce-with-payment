from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from accounts.models import UserProfile

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    # Get variations from the request
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id_list = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(set(existing_variation.values_list('id', flat=True)))
                id_list.append(item.id)

            if set([var.id for var in product_variation]) in ex_var_list:
                index = ex_var_list.index(set([var.id for var in product_variation]))
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)

                # Check if increasing quantity will exceed the available stock
                if item.quantity < product.stock and item.quantity < 10:
                    item.quantity += 1
                    item.save()
                elif item.quantity >= 10:
                    messages.info(request, "You can't add more than 10 items of this product at a time.")
                else:
                    messages.info(request, "The product's stock limit has been reached.")
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id_list = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(set(existing_variation.values_list('id', flat=True)))
                id_list.append(item.id)

            if set([var.id for var in product_variation]) in ex_var_list:
                index = ex_var_list.index(set([var.id for var in product_variation]))
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)

                # Check if increasing quantity will exceed the available stock
                if item.quantity < product.stock and item.quantity < 10:
                    item.quantity += 1
                    item.save()
                elif item.quantity >= 10:
                    messages.info(request, "You can't add more than 10 items of this product at a time.")
                else:
                    messages.info(request, "The product's stock limit has been reached.")
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id,cart_item_id):
    
    product=get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,user=cart,id=cart_item_id)
        if cart_item.quantity >  1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
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
            shipping_cost = 0
        elif total == 0:
            shipping_cost = 0
        else:
            shipping_cost = 10

        grand_total = total + tax + shipping_cost
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        shipping_cost = 0
        insufficient_stock_items = []

        if request.user.is_authenticated:
            # If user is authenticated, get their cart items
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('-created_at')
            user_profile = UserProfile.objects.get(user=request.user)
        else:
            # For anonymous users, get cart items based on cart_id
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at')

        for cart_item in cart_items:
            if cart_item.product.stock < cart_item.quantity:
                insufficient_stock_items.append(cart_item.product)
            else:
                total += cart_item.product.price * cart_item.quantity
                quantity += cart_item.quantity

        if insufficient_stock_items:
            out_of_stock_product_names = ', '.join(item.product_name for item in insufficient_stock_items)
            messages.warning(request, f"The following items are out of stock: {out_of_stock_product_names}. Please remove these from cart before checkout.")
            return redirect('cart')

        tax = (3 * total) / 100
        if total > 100:
            shipping_cost = 0
        else:
            shipping_cost = 10

        grand_total = total + tax + shipping_cost

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
        'user_profile': user_profile,
    }
    return render(request, 'store/checkout.html', context)