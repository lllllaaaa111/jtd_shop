"""
URL configuration for product_management - 商品管理模块
"""
from django.urls import path
from . import views

app_name = 'product_management'

urlpatterns = [
    # 商品分类相关
    path('category/list/', views.category_list, name='category_list'),
    
    # 商品相关
    path('list/', views.product_list, name='product_list'),
    path('detail/<int:product_id>/', views.product_detail, name='product_detail'),
]
