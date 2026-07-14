from .models import SiteSettings


def site_settings(request):
    site = SiteSettings.load()
    cart_count = 0
    if request.user.is_authenticated and hasattr(request.user, 'cart'):
        cart_count = request.user.cart.item_count
    return {
        'site_settings': site,
        'cart_count': cart_count,
    }
