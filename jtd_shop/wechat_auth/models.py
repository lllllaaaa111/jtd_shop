from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class WechatUser(models.Model):
    """微信用户模型"""
    user = models.OneToOneField('user_management.User', on_delete=models.CASCADE, related_name='wechat_user')
    openid = models.CharField(max_length=100, unique=True, verbose_name='微信OpenID')
    unionid = models.CharField(max_length=100, blank=True, null=True, verbose_name='微信UnionID')
    session_key = models.CharField(max_length=100, blank=True, null=True, verbose_name='会话密钥')
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='微信昵称')
    avatar_url = models.URLField(blank=True, null=True, verbose_name='微信头像')
    gender = models.IntegerField(default=0, verbose_name='性别')  # 0: 未知, 1: 男, 2: 女
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='国家')
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='省份')
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='城市')
    language = models.CharField(max_length=20, blank=True, null=True, verbose_name='语言')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'wechat_user'
        verbose_name = '微信用户'
        verbose_name_plural = '微信用户'
    
    def __str__(self):
        return f"{self.user.username} - {self.nickname or self.openid}"

class WechatSession(models.Model):
    """微信会话记录"""
    openid = models.CharField(max_length=100, verbose_name='微信OpenID')
    session_key = models.CharField(max_length=100, verbose_name='会话密钥')
    unionid = models.CharField(max_length=100, blank=True, null=True, verbose_name='微信UnionID')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'wechat_session'
        verbose_name = '微信会话'
        verbose_name_plural = '微信会话'
    
    def __str__(self):
        return f"{self.openid} - {self.expires_at}"
    
    @property
    def is_expired(self):
        """检查会话是否过期"""
        return timezone.now() > self.expires_at 