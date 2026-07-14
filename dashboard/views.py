from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from products.models import Product
from orders.models import Order, OrderItem


@staff_member_required
def dashboard_home(request):
    total_sales = Order.objects.filter(is_paid=True).aggregate(total=Sum('total'))['total'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(stock__lte=5, is_active=True).order_by('stock')[:10]

    top_products = (
        OrderItem.objects.values('product_name')
        .annotate(units_sold=Sum('quantity'), revenue=Sum(F('price') * F('quantity')))
        .order_by('-units_sold')[:5]
    )

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    sales_by_day = (
        Order.objects.filter(is_paid=True)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Sum('total'))
        .order_by('day')[:30]
    )

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock': low_stock,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'sales_by_day': list(sales_by_day),
    }
    return render(request, 'dashboard/home.html', context)
