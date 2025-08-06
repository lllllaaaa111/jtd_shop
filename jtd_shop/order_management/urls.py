"""
URL configuration for order_management - 订单管理模块
"""
from django.urls import path
from . import views

app_name = 'order_management'

urlpatterns = [
    # 订单相关
    path('list/', views.order_list, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # 购物车相关
    path('cart/list/', views.cart_list, name='cart_list'),
]
