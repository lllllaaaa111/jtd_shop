from django.contrib import admin
from .models import SystemConfig, OperationLog, FileUpload, DataBackup

class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['mchid', 'appid', 'serial_no', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['mchid', 'appid', 'serial_no']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('微信支付配置', {
            'fields': ('mchid', 'serial_no', 'api_v2_key', 'api_v3_key', 'is_active')
        }),
        ('微信支付证书文件', {
            'fields': ('cert_file', 'key_file'),
            'classes': ('collapse',)
        }),
        ('微信小程序配置', {
            'fields': ('appid', 'app_secret')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """只允许添加一个配置实例"""
        return not SystemConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """不允许删除配置"""
        return False

# 操作日志、文件上传、数据备份管理不在主admin中显示

# 注册核心模型到Admin
admin.site.register(SystemConfig, SystemConfigAdmin) 