from django.db import models
from django.utils import timezone
from user_management.models import User
from product_management.models import Product

class Order(models.Model):
    """订单模型"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunded', '已退款')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('bank', '银行转账'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')
    order_number = models.CharField(max_length=100, unique=True, verbose_name='订单号')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='订单状态'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        verbose_name='支付方式'
    )
    shipping_address = models.TextField(blank=True, null=True, verbose_name='发货地址')
    delivery_address = models.TextField(blank=True, null=True, verbose_name='收货地址')
    recipient_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='收件人姓名')
    recipient_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='收件人电话')
    notes = models.TextField(blank=True, null=True, verbose_name='订单备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='送达时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        db_table = 'order'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"订单 {self.order_number}"
    
    def save(self, *args, **kwargs):
        # 自动生成订单号
        if not self.order_number:
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}{self.user.id:04d}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """订单商品关联表"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField(verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计')
    
    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = '订单商品'
        db_table = 'order_item'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # 自动计算小计
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

class Cart(models.Model):
    """购物车模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品ID')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        db_table = 'cart'
        unique_together = ['user', 'product']  # 同一用户同一商品只能有一条记录
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    @property
    def total_price(self):
        """计算该购物车项的总价"""
        return self.quantity * self.product.price

class OrderStatusLog(models.Model):
    """订单状态变更日志"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs', verbose_name='订单')
    from_status = models.CharField(max_length=20, verbose_name='原状态')
    to_status = models.CharField(max_length=20, verbose_name='新状态')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '订单状态日志'
        verbose_name_plural = '订单状态日志'
        db_table = 'order_status_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.from_status} -> {self.to_status}"