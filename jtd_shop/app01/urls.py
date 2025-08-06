"""
URL configuration for app01 - 核心功能模块
"""
from django.urls import path
from .views import index, films, random_t_views

app_name = 'app01'

urlpatterns = [
    # 核心功能接口
    path('index/', index, name='index'),
    path('films/', films, name='films'),
    path('random/', random_t_views, name='random'),
]
