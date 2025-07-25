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
