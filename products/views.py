from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Wishlist, Review


def _product_list_context(request, products, page_title=None):
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    brand_slug = request.GET.get('brand')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass

    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'price_low':  'price',
        'price_high': '-price',
        'popularity': '-popularity',
        'newest':     '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return {
        'page_obj':          page_obj,
        'categories':        Category.objects.filter(is_active=True),
        'brands':            Brand.objects.filter(is_active=True),
        'query':             query,
        'selected_category': category_slug,
        'selected_brand':    brand_slug,
        'sort':              sort,
        'min_price':         min_price or '',
        'max_price':         max_price or '',
        'wishlist_ids':      wishlist_ids,
        'page_title':        page_title,
    }


def product_list(request):
    """Generic product list — used by /products/ URL."""
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/product_list.html',
                  _product_list_context(request, products))


def shop_view(request):
    """Main shop page — matches frontend/shop.html exactly."""
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/shop.html',
                  _product_list_context(request, products, page_title='Shop'))


def search_view(request):
    """Search results page."""
    products = Product.objects.filter(is_active=True)
    ctx = _product_list_context(request, products)
    return render(request, 'products/search.html', ctx)


def bestsellers_view(request):
    """Best Sellers — matches frontend/bestsellers.html exactly."""
    products = Product.objects.filter(is_active=True).order_by('-popularity')
    return render(request, 'products/bestsellers.html',
                  _product_list_context(request, products, page_title='Best Sellers'))


def new_arrivals_view(request):
    """New Arrivals — matches frontend/newarrivals.html exactly."""
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'products/new_arrivals.html',
                  _product_list_context(request, products, page_title='New Arrivals'))


def category_products(request, category_slug):
    """Generic category view — skincare/makeup/haircare each get their own template."""
    products = Product.objects.filter(is_active=True, category__slug=category_slug)
    category = Category.objects.filter(slug=category_slug, is_active=True).first()
    title = category.name if category else category_slug.title()

    template_map = {
        'skincare': 'products/skincare.html',
        'makeup':   'products/makeup.html',
        'haircare': 'products/haircare.html',
    }
    template = template_map.get(category_slug, 'products/product_list.html')

    ctx = _product_list_context(request, products, page_title=title)
    ctx['active_category'] = category
    return render(request, template, ctx)


def brands_view(request):
    """Brands page — matches frontend/brands.html exactly."""
    brands = Brand.objects.filter(is_active=True).order_by('name')
    return render(request, 'products/brands.html', {'brands': brands})


def offers_view(request):
    """Offers page — matches frontend/offers.html exactly."""
    products = Product.objects.filter(is_active=True, discount_price__isnull=False)
    ctx = _product_list_context(request, products, page_title='Special Offers')
    return render(request, 'products/offers.html', ctx)


def product_detail(request, slug):
    """Product detail page."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    Product.objects.filter(pk=product.pk).update(popularity=product.popularity + 1)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]
    in_wishlist = False
    user_review = None
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, product=product
        ).exists()
        user_review = Review.objects.filter(user=request.user, product=product).first()

    reviews = Review.objects.filter(product=product).select_related('user')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    review_count = reviews.count()

    return render(request, 'products/product_detail.html', {
        'product':      product,
        'related':      related,
        'in_wishlist':  in_wishlist,
        'reviews':      reviews,
        'user_review':  user_review,
        'avg_rating':   round(avg_rating, 1),
        'review_count': review_count,
    })


@login_required
def review_create(request, slug):
    """Create or update a review for a product."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    existing = Review.objects.filter(user=request.user, product=product).first()

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        rating = max(1, min(5, rating))  # clamp 1-5

        if existing:
            existing.rating = rating
            existing.comment = comment
            existing.save()
            messages.success(request, 'Your review has been updated.')
        else:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment,
            )
            messages.success(request, 'Thank you! Your review has been submitted.')
        return redirect('products:detail', slug=slug)

    return render(request, 'products/review_form.html', {
        'product': product,
        'existing': existing,
    })


@login_required
def review_delete(request, slug):
    """Delete the logged-in user's review for a product."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    Review.objects.filter(user=request.user, product=product).delete()
    messages.success(request, 'Your review has been removed.')
    return redirect('products:detail', slug=slug)


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'items': items})


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'"{product.name}" added to your wishlist.')
    else:
        messages.info(request, f'"{product.name}" is already in your wishlist.')
    return redirect(request.META.get('HTTP_REFERER') or 'products:list')


@login_required
def wishlist_remove(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, 'Removed from your wishlist.')
    return redirect(request.META.get('HTTP_REFERER') or 'products:wishlist')
