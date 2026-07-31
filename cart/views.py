from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = _get_or_create_cart(request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@login_required
def cart_add(request, product_id):
    if request.method != 'POST':
        return redirect('cart:detail')

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_or_create_cart(request.user)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
            messages.success(request, f'"{product.name}" quantity updated.')
        else:
            messages.warning(request, f'Sorry, only {product.stock} units of "{product.name}" are available.')
    else:
        if product.stock == 0:
            item.delete()
            messages.error(request, f'"{product.name}" is out of stock.')
        else:
            messages.success(request, f'"{product.name}" added to your cart.')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', 'cart:detail')
    return redirect(next_url)


@login_required
def cart_update(request, item_id):
    if request.method != 'POST':
        return redirect('cart:detail')

    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        item.delete()
        messages.info(request, f'"{item.product.name}" removed from cart.')
    elif quantity > item.product.stock:
        messages.warning(request, f'Only {item.product.stock} units available.')
    else:
        item.quantity = quantity
        item.save()

    return redirect('cart:detail')


@login_required
def cart_remove(request, item_id):
    if request.method != 'POST':
        return redirect('cart:detail')

    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = item.product.name
    item.delete()
    messages.success(request, f'"{product_name}" removed from your cart.')
    return redirect('cart:detail')
