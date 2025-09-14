from django.contrib import admin
from .models import Order, OrderItem, Cart, OrderStatusLog, LogisticsInfo, LogisticsStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    fields = ('from_status', 'to_status', 'operator', 'notes', 'created_at')
    readonly_fields = ('created_at',)


class LogisticsStatusLogInline(admin.TabularInline):
    model = LogisticsStatusLog
    extra = 0
    fields = ('from_status', 'to_status', 'location', 'description', 'operator', 'created_at')
    readonly_fields = ('created_at',)


class LogisticsInfoInline(admin.StackedInline):
    model = LogisticsInfo
    extra = 0
    fields = ('courier_company', 'tracking_number', 'status', 'sender_name', 'sender_phone', 
              'sender_address', 'estimated_delivery', 'actual_delivery', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    classes = ('collapse',)
    verbose_name = '物流信息'
    verbose_name_plural = '物流信息'
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    def get_queryset(self, request):
        """确保只显示当前订单的物流信息"""
        qs = super().get_queryset(request)
        return qs
    
    def get_formset(self, request, obj=None, **kwargs):
        """自定义表单集"""
        formset = super().get_formset(request, obj, **kwargs)
        formset.verbose_name = '物流信息'
        formset.verbose_name_plural = '物流信息'
        return formset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'logistics_status', 'created_at')
    list_filter = ('status', 'logistics__status', 'created_at')
    search_fields = ('order_number', 'user__username', 'recipient_name')
    ordering = ('-created_at',)
    inlines = [OrderItemInline, LogisticsInfoInline]
    readonly_fields = ('order_number', 'internal_order_number', 'created_at', 'updated_at')
    list_display_links = ('order_number',)
    list_per_page = 20
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    fieldsets = (
        ('订单信息', {
            'fields': ('order_number', 'user', 'total_amount', 'status')
        }),
        ('收货信息', {
            'fields': ('delivery_address', 'recipient_name', 'recipient_phone')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logistics_status(self, obj):
        """显示物流状态"""
        if hasattr(obj, 'logistics'):
            return obj.logistics.get_status_display()
        return '无物流信息'
    logistics_status.short_description = '物流状态'
    
    def save_model(self, request, obj, form, change):
        """保存订单时处理物流状态更新"""
        super().save_model(request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        """保存关联对象时处理物流状态变更"""
        super().save_related(request, form, formsets, change)
        
        # 处理物流信息的状态变更
        for formset in formsets:
            if formset.model == LogisticsInfo:
                for form in formset.forms:
                    if form.instance.pk and form.has_changed():
                        # 检查状态是否发生变化
                        if 'status' in form.changed_data:
                            from .models import LogisticsStatusLog
                            LogisticsStatusLog.objects.create(
                                logistics=form.instance,
                                from_status=form.initial.get('status', ''),
                                to_status=form.instance.status,
                                operator=request.user,
                                description='后台管理更新物流状态'
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
    list_per_page = 20


# 物流相关模型不在主admin中显示，通过订单内联管理 