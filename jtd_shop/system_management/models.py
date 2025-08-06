from django.db import models
from django.utils import timezone
from user_management.models import User

class SystemConfig(models.Model):
    """系统配置"""
    key = models.CharField(max_length=100, unique=True, verbose_name="配置键")
    value = models.TextField(verbose_name="配置值")
    description = models.TextField(blank=True, verbose_name="配置描述")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "系统配置"
        verbose_name_plural = "系统配置"
        db_table = 'system_config'
        ordering = ['key']
    
    def __str__(self):
        return self.key

class OperationLog(models.Model):
    """操作日志"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="操作用户")
    action = models.CharField(max_length=100, verbose_name="操作类型")
    resource = models.CharField(max_length=100, verbose_name="操作资源")
    resource_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="资源ID")
    description = models.TextField(blank=True, verbose_name="操作描述")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP地址")
    user_agent = models.TextField(blank=True, verbose_name="用户代理")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    
    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"
        db_table = 'operation_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.action} - {self.resource}"

class FileUpload(models.Model):
    """文件上传记录"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="上传用户")
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file_path = models.CharField(max_length=500, verbose_name="文件路径")
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)")
    file_type = models.CharField(max_length=100, verbose_name="文件类型")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    
    class Meta:
        verbose_name = "文件上传记录"
        verbose_name_plural = "文件上传记录"
        db_table = 'file_upload'
        ordering = ['-upload_time']
    
    def __str__(self):
        return self.file_name
    
    @property
    def file_size_mb(self):
        """文件大小(MB)"""
        return round(self.file_size / (1024 * 1024), 2)

class DataBackup(models.Model):
    """数据备份记录"""
    backup_name = models.CharField(max_length=200, verbose_name="备份名称")
    backup_type = models.CharField(max_length=50, verbose_name="备份类型")
    file_path = models.CharField(max_length=500, verbose_name="备份文件路径")
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)")
    description = models.TextField(blank=True, verbose_name="备份描述")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_success = models.BooleanField(default=True, verbose_name="是否成功")
    
    class Meta:
        verbose_name = "数据备份"
        verbose_name_plural = "数据备份"
        db_table = 'data_backup'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.backup_name