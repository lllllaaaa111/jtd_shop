from django.db import models
from django.utils import timezone
from user_management.models import User

class Welcome(models.Model):
    """欢迎页面内容"""
    title = models.CharField(max_length=200, verbose_name="标题", default="欢迎图片")
    img = models.ImageField(upload_to="welcome", default='/welcome/welcome1.jpg', verbose_name="图片")
    order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        verbose_name = "欢迎页面"
        verbose_name_plural = "欢迎页面"
        db_table = 'welcome'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

class Banner(models.Model):
    """轮播图"""
    title = models.CharField(max_length=200, verbose_name="标题")
    image = models.ImageField(upload_to="banners/", verbose_name="图片")
    link_url = models.URLField(blank=True, null=True, verbose_name="链接地址")
    order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "轮播图"
        verbose_name_plural = "轮播图"
        db_table = 'banner'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title

class Article(models.Model):
    """文章内容"""
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    summary = models.TextField(blank=True, verbose_name="摘要")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="作者")
    cover_image = models.ImageField(upload_to="articles/", blank=True, null=True, verbose_name="封面图片")
    is_published = models.BooleanField(default=False, verbose_name="是否发布")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="发布时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        db_table = 'article'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title

class Notice(models.Model):
    """系统公告"""
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    is_important = models.BooleanField(default=False, verbose_name="是否重要")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "系统公告"
        verbose_name_plural = "系统公告"
        db_table = 'notice'
        ordering = ['-is_important', '-created_at']
    
    def __str__(self):
        return self.title