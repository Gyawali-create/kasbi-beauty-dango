from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product, Wishlist
from .forms import ContactForm
from .models import SiteSettings


def home_view(request):
    featured = Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:8]
    bestsellers = Product.objects.filter(is_active=True).order_by('-popularity')[:4]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    out_of_stock = Product.objects.filter(is_active=True, stock=0).order_by('-updated_at')[:8]

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'core/home.html', {
        'featured_products': featured,
        'bestseller_products': bestsellers,
        'new_arrival_products': new_arrivals,
        'out_of_stock_products': out_of_stock,
        'wishlist_ids': wishlist_ids,
    })


def about_view(request):
    site = SiteSettings.load()
    return render(request, 'core/about.html', {'site': site})


def contact_view(request):
    site = SiteSettings.load()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you within 24 hours.")
            return redirect('core:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form, 'site': site})


def returns_view(request):
    site = SiteSettings.load()
    non_returnable_items = [
        'Opened skincare products',
        'Used makeup items',
        'Intimate care products',
        'Sale / discounted items',
        'Gift cards',
        'Free gift items',
    ]
    return_steps = [
        'Contact us via email or phone within 7 days of receiving your order.',
        'Provide your order number and reason for return.',
        'Our team will review and confirm within 24 hours.',
        'Ship the product back to our address (we share details via email).',
        'Refund is processed once we receive and inspect the item.',
    ]
    return render(request, 'core/returns.html', {
        'site': site,
        'non_returnable_items': non_returnable_items,
        'return_steps': return_steps,
    })
