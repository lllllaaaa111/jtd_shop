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
    path('detail/by-number/<str:order_number>/', views.order_by_number, name='order_by_number'),
    path('create/', views.create_order, name='create_order'),
    path('create-direct/', views.create_order_direct, name='create_order_direct'),
    path('update-status/', views.update_order_status, name='update_order_status'),
    path('search/', views.order_search, name='order_search'),
    path('delete/<int:order_id>/', views.order_delete, name='order_delete'),
    path('delete/by-number/<str:order_number>/', views.order_delete_by_number, name='order_delete_by_number'),
    
    # 购物车相关
    path('cart/list/', views.cart_list, name='cart_list'),
]
