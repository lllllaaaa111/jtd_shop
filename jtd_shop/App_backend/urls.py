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
from django.urls import path, include
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

# 导入自定义admin配置
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import admin_config

urlpatterns = [
    # Django管理后台
       path('admin/', admin.site.urls),
    
    # 核心功能模块
       path('smart/', include('app01.urls')),
    
    # 用户管理模块
    path('users/', include('user_management.urls')),
    
    # 商品管理模块
    path('products/', include('product_management.urls')),
    
    # 订单管理模块
    path('orders/', include('order_management.urls')),
    
    # 内容管理模块
    path('content/', include('content_management.urls')),
    
    # 系统管理模块
    path('system/', include('system_management.urls')),
    
    # 微信认证模块
    path('wechat/', include('wechat_auth.urls')),
    
    # 媒体文件服务
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)