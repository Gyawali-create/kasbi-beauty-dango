from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product, Category
from .forms import ContactForm
from .models import SiteSettings


def home_view(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    newest = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    return render(request, 'core/home.html', {
        'featured': featured,
        'newest': newest,
        'categories': categories,
        'site': SiteSettings.load(),
    })


def about_view(request):
    return render(request, 'core/about.html', {'site': SiteSettings.load()})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for reaching out! Our team will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form, 'site': SiteSettings.load()})
