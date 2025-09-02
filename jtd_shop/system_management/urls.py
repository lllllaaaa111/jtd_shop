"""
URL configuration for system_management - 系统管理模块
"""
from django.urls import path
from . import views

app_name = 'system_management'

urlpatterns = [
    # 微信支付配置相关
    path('wechat/config/', views.system_config_list, name='wechat_config'),
    
    # 操作日志相关
    path('log/list/', views.operation_log_list, name='operation_log_list'),
    
    # 文件上传记录相关
    path('file/list/', views.file_upload_list, name='file_upload_list'),
    
    # 数据备份相关
    path('backup/list/', views.data_backup_list, name='data_backup_list'),

    # 生成签名串
    path('signature/generate/', views.generate_signature_string, name='generate_signature_string'),

    # 微信支付：生成签名头
    path('wechat/certificate/', views.get_wechat_certificate, name='get_wechat_certificate'),
]
