from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()
    messages.success(request, f'{product.name} added to your cart.')
    return redirect(request.POST.get('next', 'cart:view'))


@login_required
@require_POST
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        item.delete()
        messages.success(request, 'Item removed from cart.')
    else:
        if quantity > item.product.stock:
            quantity = item.product.stock
            messages.warning(request, f'Only {quantity} in stock, quantity adjusted.')
        item.quantity = quantity
        item.save()
        messages.success(request, 'Cart updated.')
    return redirect('cart:view')


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:view')
