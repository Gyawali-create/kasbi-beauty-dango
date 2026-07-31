from .models import SiteSettings
from products.models import Category, Brand


def site_settings(request):
    site = SiteSettings.load()

    cart_count = 0
    if request.user.is_authenticated and hasattr(request.user, 'cart'):
        cart_count = request.user.cart.item_count

    # All active categories with their product count — used in flyout + footer
    nav_categories = (
        Category.objects
        .filter(is_active=True)
        .prefetch_related('products')
        .order_by('name')
    )

    # All active brands — used in footer / brands page
    nav_brands = Brand.objects.filter(is_active=True).order_by('name')

    return {
        'site_settings': site,
        'cart_count': cart_count,
        'nav_categories': nav_categories,
        'nav_brands': nav_brands,
    }
