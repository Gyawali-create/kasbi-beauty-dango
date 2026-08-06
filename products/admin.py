from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Category, Brand, Product, ProductImage, Wishlist, Coupon, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ('image_preview', 'image', 'alt_text')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #eee;">',
                obj.image.url
            )
        return mark_safe('<div style="width:80px;height:80px;background:#faebed;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#C97786;font-size:22px;">🖼️</div>')
    image_preview.short_description = 'Preview'


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'slug', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:8px;">',
                obj.image.url
            )
        return mark_safe('<div style="width:48px;height:48px;background:#faebed;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px;color:#C97786;">📂</div>')
    image_preview.short_description = 'Image'

    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'slug', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:contain;border-radius:8px;background:#f9f9f9;padding:4px;">',
                obj.logo.url
            )
        return mark_safe('<div style="width:48px;height:48px;background:#faebed;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px;">🏷️</div>')
    logo_preview.short_description = 'Logo'

    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'category', 'brand', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'popularity', 'created_at')
    list_filter = ('category', 'brand', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('price', 'discount_price', 'stock', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    ordering = ('-created_at',)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:contain;border-radius:8px;background:#fafafa;padding:3px;">',
                obj.thumbnail.url
            )
        return mark_safe('<div style="width:48px;height:48px;background:#faebed;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;">🧴</div>')
    thumbnail_preview.short_description = 'Photo'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'short_comment', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('product', 'user', 'created_at')

    def short_comment(self, obj):
        return obj.comment[:60] + '...' if len(obj.comment) > 60 else obj.comment
    short_comment.short_description = 'Comment'

    def has_add_permission(self, request):
        return False


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'valid_from', 'valid_until', 'times_used', 'usage_limit')
    list_filter = ('active',)
    search_fields = ('code',)
