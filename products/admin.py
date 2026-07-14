from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Wishlist, Coupon


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'popularity', 'created_at')
    list_filter = ('category', 'brand', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('price', 'discount_price', 'stock', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    ordering = ('-created_at',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'valid_from', 'valid_until', 'times_used', 'usage_limit')
    list_filter = ('active',)
    search_fields = ('code',)
