from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, Address, Mine


class UserProfileInline(admin.StackedInline):
    """用户详细信息内联编辑"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '详细信息'
    fields = ('nickname', 'bio', 'birth_date', 'gender')
    extra = 0


class AddressInline(admin.TabularInline):
    """用户地址内联编辑"""
    model = Address
    extra = 0
    fields = ('recipient', 'address', 'contact', 'is_default')
    readonly_fields = ('is_default',)


class MineInline(admin.TabularInline):
    """用户头像图片内联编辑"""
    model = Mine
    extra = 0
    fields = ('name', 'img', 'order', 'is_delete')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    inlines = [UserProfileInline, AddressInline, MineInline]
    
    # 列表页显示的字段
    list_display = (
        'id', 'username', 'email', 'phone', 'role', 
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login'
    )
    
    # 列表页可过滤的字段
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'role', 
        'date_joined', 'last_login'
    )
    
    # 搜索字段
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    
    # 排序
    ordering = ('-date_joined',)
    
    # 详情页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'email', 'phone')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'avatar', 'role')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    # 添加用户时的字段
    add_fieldsets = (
        ('基本信息', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'role'),
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        """优化查询，减少数据库查询次数"""
        return super().get_queryset(request).select_related('profile')
    
    def get_inline_instances(self, request, obj=None):
        """根据用户权限显示内联编辑"""
        if not obj:
            # 新建用户时，只显示基本信息
            return []
        return super().get_inline_instances(request, obj)


# 注意：移除了UserProfile的单独注册，现在只在User页面中作为内联编辑显示

# 地址和头像管理不在主admin中显示，通过用户内联管理


# 自定义管理页面标题
admin.site.site_header = 'JTD商店管理系统'
admin.site.site_title = 'JTD管理'
admin.site.index_title = '欢迎使用JTD商店管理系统'