from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, F, ExpressionWrapper, FloatField
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Wishlist, Review

DISCOUNT_CHOICES = [
    ('10', 'Up to -10%'),
    ('20', 'Up to -20%'),
    ('30', 'Up to -30%'),
    ('50', 'Up to -50%'),
]


def _product_list_context(request, products, page_title=None, locked_category_slug=None):
    """
    Build the shared filter/sort/paginate context.

    locked_category_slug: when set (category pages), the category is already
    pre-filtered at the call site; sidebar category checkboxes are shown but
    do NOT re-filter the queryset (the page is already scoped to that category).
    Additional brand/price/sort/search filters still work normally.
    """
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Category filter — only active on generic shop/search pages, not on
    # dedicated category pages (where the queryset is already scoped).
    selected_categories = request.GET.getlist('category')
    if selected_categories and not locked_category_slug:
        products = products.filter(category__slug__in=selected_categories)

    # Brand filter — supports multiple checkboxes
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__slug__in=selected_brands)

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            min_price = ''
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            max_price = ''

    # Discount filter — keep only products whose % off is >= min_discount
    min_discount = request.GET.get('min_discount', '').strip()
    if min_discount:
        try:
            min_pct = int(min_discount)
            # discount_price must exist and the % off must meet the threshold
            products = products.filter(
                discount_price__isnull=False,
                discount_price__lt=F('price'),
            )
            # Annotate and filter by computed percent
            products = products.annotate(
                discount_pct=ExpressionWrapper(
                    (F('price') - F('discount_price')) * 100.0 / F('price'),
                    output_field=FloatField()
                )
            ).filter(discount_pct__gte=min_pct)
        except (ValueError, TypeError):
            min_discount = ''

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
        'page_obj':            page_obj,
        'categories':          Category.objects.filter(is_active=True),
        'brands':              Brand.objects.filter(is_active=True),
        'query':               query,
        'selected_categories': selected_categories,
        # Keep singular alias for backward compat in templates
        'selected_category':   selected_categories[0] if selected_categories else (locked_category_slug or ''),
        'selected_brands':     selected_brands,
        'selected_brand':      selected_brands[0] if selected_brands else '',
        'locked_category_slug': locked_category_slug,
        'sort':                sort,
        'min_price':           min_price,
        'max_price':           max_price,
        'min_discount':        min_discount,
        'discount_choices':    DISCOUNT_CHOICES,
        'wishlist_ids':        wishlist_ids,
        'page_title':          page_title,
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
    """Best Sellers — products flagged as bestseller."""
    products = Product.objects.filter(is_active=True, is_bestseller=True).order_by('-popularity')
    return render(request, 'products/bestsellers.html',
                  _product_list_context(request, products, page_title='Best Sellers'))


def new_arrivals_view(request):
    """New Arrivals — products flagged as new arrival."""
    products = Product.objects.filter(is_active=True, is_new_arrival=True).order_by('-created_at')
    return render(request, 'products/new_arrivals.html',
                  _product_list_context(request, products, page_title='New Arrivals'))


def category_products(request, category_slug):
    """Generic category view — skincare/makeup/haircare each get their own template."""
    products = Product.objects.filter(is_active=True, category__slug=category_slug)
    category = Category.objects.filter(slug=category_slug, is_active=True).first()
    title = category.name if category else category_slug.title()

    template_map = {
        'skincare':  'products/skincare.html',
        'makeup':    'products/makeup.html',
        'hair-care': 'products/haircare.html',
    }
    template = template_map.get(category_slug, 'products/product_list.html')

    ctx = _product_list_context(request, products, page_title=title,
                                locked_category_slug=category_slug)
    ctx['active_category'] = category
    return render(request, template, ctx)


def brands_view(request):
    """Brands page — matches frontend/brands.html exactly."""
    brands = Brand.objects.filter(is_active=True).prefetch_related('categories').order_by('name')
    return render(request, 'products/brands.html', {'brands': brands})


def offers_view(request):
    """Offers page — matches frontend/offers.html exactly."""
    products = Product.objects.filter(is_active=True, discount_price__isnull=False)
    ctx = _product_list_context(request, products, page_title='Special Offers')

    # Deals of the Day — top 8 products sorted by highest discount %
    deals = (
        Product.objects
        .filter(is_active=True, discount_price__isnull=False, discount_price__lt=F('price'))
        .annotate(
            discount_pct=ExpressionWrapper(
                (F('price') - F('discount_price')) * 100.0 / F('price'),
                output_field=FloatField()
            )
        )
        .order_by('-discount_pct')[:8]
    )
    ctx['deals_products'] = deals

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    ctx['wishlist_ids'] = wishlist_ids

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

    # Per-star breakdown for review filters
    star_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}

    return render(request, 'products/product_detail.html', {
        'product':        product,
        'related':        related,
        'in_wishlist':    in_wishlist,
        'reviews':        reviews,
        'user_review':    user_review,
        'avg_rating':     round(avg_rating, 1),
        'review_count':   review_count,
        'five_star_count':  star_counts[5],
        'four_star_count':  star_counts[4],
        'three_star_count': star_counts[3],
        'two_star_count':   star_counts[2],
        'one_star_count':   star_counts[1],
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
