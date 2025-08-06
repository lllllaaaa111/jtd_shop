from django.contrib import admin
from .models import SystemConfig, OperationLog, FileUpload, DataBackup


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    list_editable = ('is_active',)
    fieldsets = (
        ('配置信息', {
            'fields': ('key', 'value', 'description')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource', 'resource_id', 'ip_address', 'created_at')
    list_filter = ('action', 'resource', 'created_at')
    search_fields = ('user__username', 'action', 'resource', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('操作信息', {
            'fields': ('user', 'action', 'resource', 'resource_id', 'description')
        }),
        ('请求信息', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('时间', {
            'fields': ('created_at',)
        }),
    )


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_type', 'file_size_mb', 'user', 'upload_time', 'is_deleted')
    list_filter = ('file_type', 'upload_time', 'is_deleted')
    search_fields = ('file_name', 'user__username')
    ordering = ('-upload_time',)
    list_editable = ('is_deleted',)
    readonly_fields = ('file_size_mb', 'upload_time')
    fieldsets = (
        ('文件信息', {
            'fields': ('file_name', 'file_path', 'file_type', 'file_size', 'file_size_mb')
        }),
        ('上传信息', {
            'fields': ('user', 'upload_time')
        }),
        ('状态', {
            'fields': ('is_deleted',)
        }),
    )


@admin.register(DataBackup)
class DataBackupAdmin(admin.ModelAdmin):
    list_display = ('backup_name', 'backup_type', 'file_size', 'created_by', 'is_success', 'created_at')
    list_filter = ('backup_type', 'is_success', 'created_at')
    search_fields = ('backup_name', 'description', 'created_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('备份信息', {
            'fields': ('backup_name', 'backup_type', 'file_path', 'file_size', 'description')
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at')
        }),
        ('状态', {
            'fields': ('is_success',)
        }),
    ) 