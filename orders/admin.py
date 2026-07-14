from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')
    can_delete = False


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'total', 'status', 'payment_method', 'is_paid', 'created_at')
    list_filter = ('status', 'payment_method', 'is_paid')
    search_fields = ('order_number', 'user__username', 'full_name', 'phone')
    list_editable = ('status', 'is_paid')
    readonly_fields = ('order_number', 'subtotal', 'discount_amount', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentInline]
    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('order__order_number', 'transaction_id')
