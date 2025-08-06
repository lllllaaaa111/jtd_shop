from django.contrib import admin
from .models import Welcome, Banner, Article, Notice


@admin.register(Welcome)
class WelcomeAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'is_delete', 'created_at')
    list_filter = ('is_active', 'is_delete', 'created_at')
    search_fields = ('title',)
    ordering = ('order', '-created_at')
    list_editable = ('order', 'is_active')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'start_time', 'end_time', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    ordering = ('order', '-created_at')
    list_editable = ('order', 'is_active')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'image', 'link_url')
        }),
        ('显示设置', {
            'fields': ('order', 'is_active', 'start_time', 'end_time')
        }),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'published_at', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-published_at', '-created_at')
    list_editable = ('is_published',)
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'summary', 'author', 'cover_image')
        }),
        ('发布设置', {
            'fields': ('is_published', 'published_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_important', 'is_active', 'start_time', 'end_time', 'created_at')
    list_filter = ('is_important', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-is_important', '-created_at')
    list_editable = ('is_important', 'is_active')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content')
        }),
        ('显示设置', {
            'fields': ('is_important', 'is_active', 'start_time', 'end_time')
        }),
    ) 