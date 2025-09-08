"""
URL configuration for user_management - 用户管理模块
"""
from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    # CSRF认证相关
    path('csrf/token/', views.get_csrf_token, name='get_csrf_token'),           # 获取CSRF令牌
    path('csrf/validate/', views.validate_csrf_token, name='validate_csrf_token'), # 验证CSRF令牌
    path('csrf/info/', views.csrf_info, name='csrf_info'),                     # 获取CSRF信息
    
    # 认证相关
    path('login/', views.user_login, name='user_login'),                    #用户登录
    path('register/', views.user_register, name='user_register'),           #用户注册
    path('logout/', views.user_logout, name='user_logout'),                 #用户登出
    path('info/', views.user_info, name='user_info'),                       #获取当前用户信息
    
    # 用户管理相关
    path('list/', views.user_list, name='user_list'),                               #用户列表
    path('detail/<int:user_id>/', views.user_detail, name='user_detail'),            #用户详情
    path('create/', views.user_create, name='user_create'),                          #创建用户
    path('update/<int:user_id>/', views.user_update, name='user_update'),             #更新用户
    path('delete/<int:user_id>/', views.user_delete, name='user_delete'),             #删除用户
    
    # 地址管理相关
    path('address/', views.address_list, name='address_list'),                        #地址列表（当前用户）
    path('address/<int:address_id>/', views.address_detail, name='address_detail'),   #地址详情
    path('address/create/', views.address_create, name='address_create'),             #创建地址
    path('address/update/<int:address_id>/', views.address_update, name='address_update'), #更新地址
    path('address/delete/<int:address_id>/', views.address_delete, name='address_delete'), #删除地址
    
    # 头像管理相关
    path('avatar/', views.get_user_mine, name='get_user_avatar'),                    #获取用户头像
    path('avatar/list/', views.mine_image_list, name='avatar_list'),                  #获取用户头像列表
    path('avatar/upload/', views.upload_mine_image, name='upload_avatar'),            #上传用户头像
    path('avatar/delete/', views.delete_mine_image, name='delete_avatar'),            #删除用户头像
    path('avatar/set/', views.set_mine_avatar, name='set_avatar'),                    #设置用户头像

    #  aes解密得到
    path('aes/phone/', views.aes_phone, name='aes_phone'),                       #电话号码解密
]
