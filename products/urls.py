from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('shop/', views.shop_view, name='shop'),
    path('bestsellers/', views.bestsellers_view, name='bestsellers'),
    path('brands/', views.brands_view, name='brands'),
    path('offers/', views.offers_view, name='offers'),
    path('skincare/', views.category_products, {'category_slug': 'skincare'}, name='skincare'),
    path('haircare/', views.category_products, {'category_slug': 'haircare'}, name='haircare'),
    path('makeup/', views.category_products, {'category_slug': 'makeup'}, name='makeup'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('<slug:slug>/', views.product_detail, name='detail'),
]