from django.db import models
from django.utils import timezone
from user_management.models import User

class SystemConfig(models.Model):
    """微信支付系统配置"""
    mchid = models.CharField(max_length=50, verbose_name="微信支付商户号", help_text="微信支付商户号", default="", blank=True)
    serial_no = models.CharField(max_length=100, verbose_name="商户API证书序列号", help_text="商户API证书序列号", default="", blank=True)
    api_v2_key = models.TextField(verbose_name="API v2私钥", help_text="微信支付API v2私钥", default="", blank=True)
    api_v3_key = models.CharField(max_length=100, verbose_name="API V3密钥", help_text="微信支付API V3密钥", default="", blank=True)
    cert_file = models.TextField(verbose_name="微信支付证书文件", help_text="微信支付证书文件内容（PEM格式）", default="", blank=True)
    key_file = models.TextField(verbose_name="微信支付私钥文件", help_text="微信支付私钥文件内容（PEM格式）", default="", blank=True)
    appid = models.CharField(max_length=50, verbose_name="微信小程序AppID", help_text="微信小程序AppID", default="", blank=True)
    app_secret = models.CharField(max_length=100, verbose_name="微信小程序AppSecret", help_text="微信小程序AppSecret", default="", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "微信支付配置"
        verbose_name_plural = "微信支付配置"
        db_table = 'system_config'
    
    def __str__(self):
        return f"微信支付配置 - {self.mchid}"
    
    @classmethod
    def get_wechat_pay_config(cls):
        """获取微信支付配置"""
        try:
            config = cls.objects.filter(is_active=True).first()
            if config:
                return {
                    'mchid': config.mchid,
                    'serial_no': config.serial_no,
                    'api_v2_key': config.api_v2_key,
                    'api_v3_key': config.api_v3_key,
                    'cert_file': config.cert_file,
                    'key_file': config.key_file,
                    'appid': config.appid,
                    'app_secret': config.app_secret
                }
            return {}
        except Exception:
            return {}
    
    @classmethod
    def get_config_value(cls, key, default=None):
        """获取指定配置的值"""
        try:
            config = cls.objects.filter(is_active=True).first()
            if config and hasattr(config, key):
                return getattr(config, key)
            return default
        except Exception:
            return default


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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_success = models.BooleanField(default=True, verbose_name="是否成功")
    
    class Meta:
        verbose_name = "数据备份"
        verbose_name_plural = "数据备份"
        db_table = 'data_backup'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.backup_name
