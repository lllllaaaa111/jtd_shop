"""
URL configuration for wechat_auth - 微信认证模块
"""
from django.urls import path
from . import views

app_name = 'wechat_auth'

urlpatterns = [
    # 微信登录相关
    path('login/', views.wechat_login, name='wechat_login'),                    # 微信登录（包含用户信息）
    path('code-login/', views.wechat_code_login, name='wechat_code_login'),     # 仅code登录
    path('user-info/', views.get_wechat_user_info, name='get_wechat_user_info'), # 获取微信用户信息
    path('update-user-info/', views.update_wechat_user_info, name='update_wechat_user_info'), # 更新微信用户信息
    path('access-token/', views.wechat_access_token, name='wechat_access_token'), # 获取access_token
] 