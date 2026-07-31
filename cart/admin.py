from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'added_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total', 'updated_at')
    readonly_fields = ('user', 'created_at', 'updated_at')
    inlines = [CartItemInline]

    def has_add_permission(self, request):
        # Carts are created automatically when users register — never add manually
        return False

    def has_delete_permission(self, request, obj=None):
        return False
