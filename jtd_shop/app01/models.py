from django.utils import timezone
from django.db import models
from django.conf import settings
import uuid
# Create your models here.
# models.py
class Welcome(models.Model):
    """
    Welcome 页面
    """
    img = models.ImageField(upload_to="welcome", default='/welcome/welcome1.jpg')
    order = models.IntegerField(default=0)

    # 修改为 created_at
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_delete = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "欢迎表"


class Mine(models.Model):
    """
    Mine 页面 - 用户个人图片
    """
    name = models.CharField(max_length=100, verbose_name="图片名称", blank=True, null=True)
    img = models.ImageField(upload_to="mine", verbose_name="图片")
    order = models.IntegerField(default=0, verbose_name="排序")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="已删除")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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

    def save(self, *args, ** kwargs):
        # 先保存以生成 created_at
        if self.id is None:
            super().save(*args,  ** kwargs)

            # 设置默认名称
            if not self.name:
                self.name = f"头像 {self.created_at.strftime('%Y-%m-%d')}"

            # 再次保存以更新名称
            super().save(*args, ** kwargs)

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
# app01/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """用户模型"""
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='电话')
    password = models.CharField(max_length=128, verbose_name='密码')
    role = models.CharField(
        max_length=20, 
        choices=[('admin', '管理员'), ('user', '普通用户')],
        default='user',
        verbose_name='权限'
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'user'
    
    def __str__(self):
        return self.username

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

class ProductCategory(models.Model):
    """商品种类模型"""
    category_name = models.CharField(max_length=100, verbose_name='类别名称')
    description = models.TextField(blank=True, null=True, verbose_name='详情')
    
    class Meta:
        verbose_name = '商品种类'
        verbose_name_plural = '商品种类'
        db_table = 'product_category'
    
    def __str__(self):
        return self.category_name

class Product(models.Model):
    """商品本身表模型"""
    name = models.CharField(max_length=200, verbose_name='名称')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    manufacturer = models.CharField(max_length=200, verbose_name='生产单位')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    description_image = models.ImageField(
        upload_to='products/descriptions/', 
        blank=True, 
        null=True, 
        verbose_name='相关介绍图片'
    )
    cover_image = models.ImageField(
        upload_to='products/covers/', 
        blank=True, 
        null=True, 
        verbose_name='封面图片'
    )
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.CASCADE, 
        verbose_name='商品类别ID'
    )
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        db_table = 'product'
    
    def __str__(self):
        return self.name

# 在 app01/models.py 中修改 Order 模型
class Order(models.Model):
    """订单模型"""
    STATUS_CHOICES = [
        ('paid', '已支付'),
        ('completed', '未完成'),
        ('cancelled', '退款')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')
    shipping_address = models.TextField(blank=True, null=True, verbose_name='发货地址')  # 允许为空
    delivery_address = models.TextField(blank=True, null=True, verbose_name='收货地址')  # 允许为空
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='支付方式')  # 允许为空
    order_number = models.CharField(max_length=100, unique=True, verbose_name='订单号')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='paid',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        db_table = 'order'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"订单 {self.order_number}"

class Cart(models.Model):
    """购物车模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品ID')
    added_at = models.DateTimeField(default=timezone.now, verbose_name='商品添加时间')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    
    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        db_table = 'cart'
        unique_together = ['user', 'product']  # 同一用户同一商品只能有一条记录
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    @property
    def total_price(self):
        """计算该购物车项的总价"""
        return self.quantity * self.price

class OrderItem(models.Model):
    """订单商品关联表（根据ER图中订单和商品的多对多关系添加）"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField(verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    
    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = '订单商品'
        db_table = 'order_item'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"
    
    @property
    def total_price(self):
        """计算该订单项的总价"""
        return self.quantity * self.price