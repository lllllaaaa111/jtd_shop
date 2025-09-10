from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    """用户模型"""
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='电话')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    role = models.CharField(
        max_length=20, 
        choices=[('admin', '管理员'), ('user', '普通用户'), ('vip', 'VIP用户')],
        default='user',
        verbose_name='用户角色'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'user'
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    """用户详细信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    birth_date = models.DateField(null=True, blank=True, verbose_name='生日')
    gender = models.CharField(
        max_length=10,
        choices=[('male', '男'), ('female', '女'), ('other', '其他')],
        default='other',
        verbose_name='性别'
    )
    
    class Meta:
        verbose_name = '用户详细信息'
        verbose_name_plural = '用户详细信息'
        db_table = 'user_profile'
    
    def __str__(self):
        return f"{self.user.username}的详细信息"

class Address(models.Model):
    """地址模型"""
    recipient = models.CharField(max_length=100, verbose_name='收件人')
    address = models.TextField(verbose_name='收件地址')
    contact = models.CharField(max_length=20, verbose_name='联系方式')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')
    
    class Meta:
        verbose_name = '地址'
        verbose_name_plural = '地址'
        db_table = 'address'
    
    def __str__(self):
        return f"{self.recipient} - {self.address}"

class Mine(models.Model):
    """用户个人图片/头像"""
    name = models.CharField(max_length=100, verbose_name="图片名称", blank=True, null=True)
    img = models.ImageField(upload_to="mine", verbose_name="图片")
    order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="已删除")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="关联用户",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "个人页图片"
        ordering = ['order']

    def __str__(self):
        return self.name or f"未命名图片 ({self.created_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        # 先保存以生成 created_at
        if self.id is None:
            super().save(*args, **kwargs)

            # 设置默认名称
            if not self.name:
                self.name = f"头像 {self.created_at.strftime('%Y-%m-%d')}"

            # 再次保存以更新名称
            super().save(*args, **kwargs)

    @property
    def file_size(self):
        """返回文件大小（友好格式）"""
        if self.img:
            size_bytes = self.img.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        return "0 B"

class WechatSession(models.Model):
    """微信小程序登录会话（Cookie版，独立于 wechat_auth.WechatSession）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wx_sessions', verbose_name='用户')
    openid = models.CharField(max_length=64, db_index=True, verbose_name='OpenID')
    wx_session_key = models.CharField(max_length=128, verbose_name='微信session_key')
    session_cookie = models.CharField(max_length=64, db_index=True, verbose_name='会话Cookie值')
    cookie_expires_at = models.DateTimeField(verbose_name='Cookie过期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '微信会话(Cookie)'
        verbose_name_plural = '微信会话(Cookie)'
        db_table = 'wechat_session_cookie'
        indexes = [models.Index(fields=['openid', 'session_cookie'])]