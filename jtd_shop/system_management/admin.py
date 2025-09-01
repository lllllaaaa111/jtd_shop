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

class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource', 'resource_id', 'ip_address', 'created_at']
    list_filter = ['action', 'resource', 'created_at']
    search_fields = ['user__username', 'action', 'resource', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'file_size_mb', 'user', 'upload_time', 'is_deleted']
    list_filter = ['file_type', 'is_deleted', 'upload_time']
    search_fields = ['file_name', 'user__username']
    readonly_fields = ['upload_time', 'file_size']
    ordering = ['-upload_time']
    date_hierarchy = 'upload_time'

class DataBackupAdmin(admin.ModelAdmin):
    list_display = ['backup_name', 'backup_type', 'file_size', 'created_by', 'created_at', 'is_success']
    list_filter = ['backup_type', 'is_success', 'created_at']
    search_fields = ['backup_name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'file_size']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

# 注册所有模型到Admin
admin.site.register(SystemConfig, SystemConfigAdmin)
admin.site.register(OperationLog, OperationLogAdmin)
admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(DataBackup, DataBackupAdmin) 