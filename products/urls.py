from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Generic list (used as fallback / search redirect target)
    path('', views.product_list, name='list'),

    # Main shop page — matches frontend/shop.html
    path('shop/', views.shop_view, name='shop'),

    # Search
    path('search/', views.search_view, name='search'),

    # Category pages — each has its own template with matching banner
    path('skincare/',     views.category_products, {'category_slug': 'skincare'},  name='skincare'),
    path('haircare/',     views.category_products, {'category_slug': 'hair-care'},  name='haircare'),
    path('makeup/',       views.category_products, {'category_slug': 'makeup'},    name='makeup'),

    # Special pages
    path('bestsellers/',  views.bestsellers_view,   name='bestsellers'),
    path('new-arrivals/', views.new_arrivals_view,  name='new_arrivals'),
    path('brands/',       views.brands_view,         name='brands'),
    path('offers/',       views.offers_view,          name='offers'),

    # Wishlist
    path('wishlist/',                       views.wishlist_view,   name='wishlist'),
    path('wishlist/add/<int:product_id>/',  views.wishlist_add,    name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),

    # Reviews
    path('<slug:slug>/review/', views.review_create, name='review_create'),
    path('<slug:slug>/review/delete/', views.review_delete, name='review_delete'),

    # Product detail (must be last — slug catches everything)
    path('<slug:slug>/', views.product_detail, name='detail'),
]
