from django.contrib import admin
from .models import Order, OrderItem, Cart, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    fields = ('from_status', 'to_status', 'operator', 'notes', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'recipient_name')
    ordering = ('-created_at',)
    inlines = [OrderItemInline, OrderStatusLogInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    fieldsets = (
        ('订单信息', {
            'fields': ('order_number', 'user', 'total_amount', 'status')
        }),
        ('支付信息', {
            'fields': ('payment_method', 'paid_at')
        }),
        ('地址信息', {
            'fields': ('shipping_address', 'delivery_address', 'recipient_name', 'recipient_phone')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_at', 'updated_at', 'shipped_at', 'delivered_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    ordering = ('-order__created_at',)
    readonly_fields = ('total_price',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_at',)
    readonly_fields = ('total_price',)


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'from_status', 'to_status', 'operator', 'created_at')
    list_filter = ('from_status', 'to_status', 'created_at')
    search_fields = ('order__order_number', 'operator__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',) 