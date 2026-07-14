from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Wishlist


def product_list(request):
    products = Product.objects.filter(is_active=True)

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    brand_slug = request.GET.get('brand')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'price_low': 'price',
        'price_high': '-price',
        'popularity': '-popularity',
        'newest': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
        'query': query,
        'selected_category': category_slug,
        'selected_brand': brand_slug,
        'sort': sort,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'wishlist_ids': wishlist_ids,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    Product.objects.filter(pk=product.pk).update(popularity=product.popularity + 1)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related': related,
        'in_wishlist': in_wishlist,
    })


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'items': items})


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.name} added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'products:list'))


@login_required
def wishlist_remove(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, 'Removed from your wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'products:wishlist'))
