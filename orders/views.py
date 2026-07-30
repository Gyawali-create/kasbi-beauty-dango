from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from products.models import Coupon
from .models import Order, OrderItem, Payment
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:detail')

    if cart.items.count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user

            # Calculate totals
            order.subtotal = cart.total
            order.discount_amount = 0

            # Handle coupon
            coupon_code = form.cleaned_data.get('coupon_code', '').strip()
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code)
                    if coupon.is_valid():
                        order.coupon = coupon
                        order.discount_amount = (order.subtotal * coupon.discount_percent) / 100
                        coupon.times_used += 1
                        coupon.save()
                        messages.success(request, f'Coupon "{coupon.code}" applied! You saved Rs.{order.discount_amount:.2f}')
                    else:
                        messages.warning(request, f'Coupon "{coupon_code}" is expired or invalid.')
                except Coupon.DoesNotExist:
                    messages.warning(request, f'Coupon "{coupon_code}" not found.')

            order.total = order.subtotal - order.discount_amount
            order.save()

            # Create order items from cart
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.current_price,
                    quantity=cart_item.quantity
                )

            # Create payment record
            Payment.objects.create(
                order=order,
                amount=order.total,
                method=order.payment_method,
                status='pending' if order.payment_method != 'cod' else 'success'
            )

            # Clear cart
            cart.items.all().delete()

            messages.success(request, f'Order #{order.order_number} placed successfully! We will contact you soon.')
            return redirect('orders:history')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill from user profile if available
        initial = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial = {
                'full_name': f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username,
                'phone': profile.phone,
                'address_line': profile.address_line,
                'city': profile.city,
                'postal_code': profile.postal_code,
                'country': profile.country or 'Nepal',
            }
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
