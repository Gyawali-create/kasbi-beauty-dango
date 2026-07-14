from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from cart.models import Cart
from products.models import Coupon
from .forms import CheckoutForm
from .models import Order, OrderItem, Payment


@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('products:list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                subtotal = cart.total
                discount = Decimal('0')

                code = form.cleaned_data.get('coupon_code', '').strip()
                coupon = None
                if code:
                    try:
                        coupon = Coupon.objects.get(code__iexact=code)
                        if coupon.is_valid():
                            discount = subtotal * Decimal(coupon.discount_percent) / Decimal('100')
                        else:
                            messages.warning(request, 'Coupon is not valid or has expired.')
                            coupon = None
                    except Coupon.DoesNotExist:
                        messages.warning(request, 'Coupon code not found.')

                order.coupon = coupon
                order.subtotal = subtotal
                order.discount_amount = discount
                order.total = subtotal - discount
                order.save()

                for item in cart.items.select_related('product'):
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.current_price,
                        quantity=item.quantity,
                    )
                    item.product.stock = max(item.product.stock - item.quantity, 0)
                    item.product.popularity += item.quantity
                    item.product.save(update_fields=['stock', 'popularity'])

                Payment.objects.create(
                    order=order,
                    amount=order.total,
                    method=order.payment_method,
                    status='success' if order.payment_method != 'cod' else 'pending',
                )
                if order.payment_method != 'cod':
                    order.is_paid = True
                    order.save(update_fields=['is_paid'])

                if coupon:
                    coupon.times_used += 1
                    coupon.save(update_fields=['times_used'])

                cart.items.all().delete()

            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('orders:detail', order_number=order.order_number)
    else:
        initial = {}
        if hasattr(request.user, 'profile'):
            p = request.user.profile
            initial = {
                'full_name': request.user.get_full_name() or request.user.username,
                'phone': p.phone,
                'address_line': p.address_line,
                'city': p.city,
                'postal_code': p.postal_code,
                'country': p.country or 'Nepal',
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
