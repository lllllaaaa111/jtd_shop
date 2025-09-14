"""
Django Admin 配置 - 只显示核心表
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

# 导入需要显示的核心模型
from user_management.models import User
from product_management.models import Product, Category
from order_management.models import Order, Cart
from content_management.models import Welcome
from system_management.models import SystemConfig

# 导入对应的Admin类
from user_management.admin import UserAdmin
from product_management.admin import ProductAdmin, CategoryAdmin
from order_management.admin import OrderAdmin, CartAdmin
from content_management.admin import WelcomeAdmin
from system_management.admin import SystemConfigAdmin

def setup_admin():
    """设置Django Admin只显示核心表"""
    
    # 清空所有已注册的模型
    admin.site._registry.clear()
    
    # 注册核心模型
    admin.site.register(User, UserAdmin)
    admin.site.register(Group, GroupAdmin)
    admin.site.register(Product, ProductAdmin)
    admin.site.register(Category, CategoryAdmin)
    admin.site.register(Order, OrderAdmin)
    admin.site.register(Cart, CartAdmin)
    admin.site.register(Welcome, WelcomeAdmin)
    admin.site.register(SystemConfig, SystemConfigAdmin)
    
    # 设置站点标题
    admin.site.site_header = 'JTD商城管理系统'
    admin.site.site_title = 'JTD管理'
    admin.site.index_title = '欢迎使用JTD商城管理系统'

# 在Django启动时调用
setup_admin()
