"""
URL configuration for App_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.static import serve

from django.conf import settings
from app01.views import index, films, random_t_views, welcome_image_list
from .views import welcome, mine, upload_mine_image, mine_image_list, get_user_mine, delete_mine_image, set_mine_avatar
urlpatterns = [
       path('welcome/', welcome_image_list, name='welcome_image_list'),
       path('mine/', get_user_mine, name='get_mine_image'),

       path('mine/list/', mine_image_list, name='mine_list'),
       # path('mine/', mine),
       path('mine/upload/', upload_mine_image, name='upload_mine_image'),

       path('mine/upload/', upload_mine_image, name='upload_mine_image'),

       path('mine/delete/', delete_mine_image, name='delete_mine_image'),
# 添加设置头像路由
       path('mine/set/', set_mine_avatar, name='set_mine_avatar'),
]
