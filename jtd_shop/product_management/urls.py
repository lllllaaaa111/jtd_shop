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
    path('create/', views.product_create, name='product_create'),
    path('search/', views.product_search_by_name, name='product_search_by_name'),
    
    # 根据分类获取商品
    path('by-category/', views.products_by_category, name='products_by_category'),           # 模糊匹配分类名称
    path('by-category/<str:category_name>/', views.products_by_category_exact, name='products_by_category_exact'),  # 精确匹配分类名称
]
