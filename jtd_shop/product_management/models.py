from django.db import models
from django.utils import timezone
from user_management.models import User

class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父分类')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        db_table = 'product_category'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """商品模型"""
    name = models.CharField(max_length=200, verbose_name='商品名称')
    description = models.TextField(blank=True, verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    manufacturer = models.CharField(max_length=200, verbose_name='生产单位')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='商品分类')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        db_table = 'product'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """商品图片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField(upload_to='products/', verbose_name='图片')
    is_primary = models.BooleanField(default=False, verbose_name='是否主图')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'
        db_table = 'product_image'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.product.name}的图片"

class ProductDescription(models.Model):
    """商品描述图片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='descriptions', verbose_name='商品')
    description_image = models.ImageField(
        upload_to='products/descriptions/', 
        blank=True, 
        null=True, 
        verbose_name='相关介绍图片'
    )
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品描述图片'
        verbose_name_plural = '商品描述图片'
        db_table = 'product_description'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.product.name}的描述图片"