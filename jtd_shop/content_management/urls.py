"""
URL configuration for content_management - 内容管理模块
"""
from django.urls import path
from . import views

app_name = 'content_management'

urlpatterns = [
    # 欢迎页面相关
    path('welcome/', views.welcome, name='welcome'),
    path('welcome/list/', views.welcome_image_list, name='welcome_list'),
    
    # 轮播图相关
    path('banner/list/', views.banner_list, name='banner_list'),
    
    # 文章相关
    path('article/list/', views.article_list, name='article_list'),
    path('article/detail/<int:article_id>/', views.article_detail, name='article_detail'),
    
    # 系统公告相关
    path('notice/list/', views.notice_list, name='notice_list'),
]
