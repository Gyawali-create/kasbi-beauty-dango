from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import hmac, hashlib, base64, uuid, json, requests as http_requests
from cart.models import Cart
from products.models import Coupon
from .models import Order, OrderItem, Payment
from .forms import CheckoutForm


# ── helpers ──────────────────────────────────────────────────────────────────

def _esewa_signature(total_amount, transaction_uuid, product_code):
    """Generate HMAC-SHA256 base64 signature for eSewa."""
    message = f'total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}'
    key = settings.ESEWA_SECRET_KEY.encode('utf-8')
    sig = hmac.new(key, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(sig).decode('utf-8')


# ── checkout ─────────────────────────────────────────────────────────────────

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
            order.subtotal = cart.total
            order.discount_amount = 0

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

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.current_price,
                    quantity=cart_item.quantity,
                )

            # COD → immediate success payment record
            if order.payment_method == 'cod':
                Payment.objects.create(
                    order=order, amount=order.total,
                    method='cod', status='success',
                )
                cart.items.all().delete()
                messages.success(request, f'Order #{order.order_number} placed! We will contact you soon.')
                return redirect('orders:history')

            # eSewa → redirect to eSewa payment page
            elif order.payment_method == 'esewa':
                Payment.objects.create(
                    order=order, amount=order.total,
                    method='esewa', status='pending',
                )
                cart.items.all().delete()
                return redirect('orders:esewa_initiate', order_number=order.order_number)

            # Other online methods → pending
            else:
                Payment.objects.create(
                    order=order, amount=order.total,
                    method=order.payment_method, status='pending',
                )
                cart.items.all().delete()
                messages.success(request, f'Order #{order.order_number} placed! Payment pending.')
                return redirect('orders:history')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
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


# ── eSewa ─────────────────────────────────────────────────────────────────────

@login_required
def esewa_initiate(request, order_number):
    """Render a page that auto-submits the eSewa payment form."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Generate a NEW unique transaction UUID every attempt
    # Using order_number + timestamp so eSewa never sees a duplicate
    import datetime
    timestamp = datetime.datetime.now().strftime('%m%d%H%M%S')
    transaction_uuid = f'{order.order_number}-{timestamp}'

    total_amount = str(order.total)
    product_code = settings.ESEWA_PRODUCT_CODE
    signature = _esewa_signature(total_amount, transaction_uuid, product_code)
    base = settings.ESEWA_BASE_URL

    # Update or create the pending payment record with the new UUID
    payment, _ = Payment.objects.update_or_create(
        order=order,
        defaults={
            'amount': order.total,
            'method': 'esewa',
            'status': 'pending',
            'transaction_id': transaction_uuid,
        }
    )

    context = {
        'order': order,
        'esewa_url': settings.ESEWA_PAYMENT_URL,
        'amount': str(order.total),
        'tax_amount': '0',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': f'{base}/orders/esewa/success/',
        'failure_url': f'{base}/orders/esewa/failure/',
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
    }
    return render(request, 'orders/esewa_initiate.html', context)


@csrf_exempt
def esewa_success(request):
    """eSewa redirects here after successful payment with base64 encoded data."""
    encoded = request.GET.get('data', '')
    if not encoded:
        messages.error(request, 'Invalid eSewa response.')
        return redirect('orders:history')

    try:
        decoded = json.loads(base64.b64decode(encoded).decode('utf-8'))
        status = decoded.get('status')
        transaction_uuid = decoded.get('transaction_uuid')
        total_amount = decoded.get('total_amount')
        transaction_code = decoded.get('transaction_code', '')

        # Verify signature
        received_sig = decoded.get('signature', '')
        signed_fields = decoded.get('signed_field_names', '')
        fields = [f.strip() for f in signed_fields.split(',')]
        message = ','.join(f'{f}={decoded.get(f, "")}' for f in fields)
        key = settings.ESEWA_SECRET_KEY.encode('utf-8')
        expected_sig = base64.b64encode(
            hmac.new(key, message.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        if received_sig != expected_sig:
            messages.error(request, 'eSewa payment verification failed. Please contact support.')
            return redirect('orders:history')

        if status == 'COMPLETE':
            order = get_object_or_404(Order, order_number=transaction_uuid)
            order.is_paid = True
            order.status = 'processing'
            order.save()
            payment = order.payment
            payment.status = 'success'
            payment.transaction_id = transaction_code
            payment.save()
            messages.success(request, f'Payment successful! Order #{order.order_number} confirmed.')
            return redirect('orders:detail', order_number=order.order_number)
        else:
            messages.warning(request, f'eSewa payment status: {status}. Please contact support.')
            return redirect('orders:history')

    except Exception as e:
        messages.error(request, f'Error processing eSewa response: {str(e)}')
        return redirect('orders:history')


@csrf_exempt
def esewa_failure(request):
    """eSewa redirects here on failure or cancellation."""
    messages.error(request, 'eSewa payment was cancelled or failed. Please try again.')
    return redirect('orders:history')


# ── order history / detail ────────────────────────────────────────────────────

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
