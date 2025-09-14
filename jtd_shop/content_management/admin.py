from django.contrib import admin
from .models import Welcome, Banner, Article, Notice


@admin.register(Welcome)
class WelcomeAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'is_delete', 'created_at')
    list_filter = ('is_active', 'is_delete', 'created_at')
    search_fields = ('title',)
    ordering = ('order', '-created_at')
    list_editable = ('order', 'is_active')


# 横幅、文章、公告管理不在主admin中显示 