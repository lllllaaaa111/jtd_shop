from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SystemConfig, OperationLog, FileUpload, DataBackup
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_config_list(request):
    """获取系统配置列表"""
    try:
        configs = SystemConfig.objects.filter(is_active=True).order_by('key')
        data = []
        for config in configs:
            data.append({
                'id': config.id,
                'key': config.key,
                'value': config.value,
                'description': config.description,
                'updated_at': config.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取系统配置列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def operation_log_list(request):
    """获取操作日志列表"""
    try:
        logs = OperationLog.objects.all().order_by('-created_at')[:100]  # 限制返回最近100条
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'user': log.user.username if log.user else 'Anonymous',
                'action': log.action,
                'resource': log.resource,
                'resource_id': log.resource_id,
                'description': log.description,
                'ip_address': log.ip_address,
                'created_at': log.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取操作日志列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def file_upload_list(request):
    """获取文件上传记录列表"""
    try:
        files = FileUpload.objects.filter(is_deleted=False).order_by('-upload_time')
        data = []
        for file in files:
            data.append({
                'id': file.id,
                'file_name': file.file_name,
                'file_path': file.file_path,
                'file_size': file.file_size,
                'file_size_mb': file.file_size_mb,
                'file_type': file.file_type,
                'upload_time': file.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                'user': file.user.username if file.user else 'Anonymous'
            })
        
            return Response({
                'code': 200,
            'msg': 'success',
            'result': data
            })
    except Exception as e:
        logger.exception("获取文件上传记录列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def data_backup_list(request):
    """获取数据备份记录列表"""
    try:
        backups = DataBackup.objects.all().order_by('-created_at')
        data = []
        for backup in backups:
            data.append({
                'id': backup.id,
                'backup_name': backup.backup_name,
                'backup_type': backup.backup_type,
                'file_path': backup.file_path,
                'file_size': backup.file_size,
                'description': backup.description,
                'created_by': backup.created_by.username if backup.created_by else 'System',
                'created_at': backup.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_success': backup.is_success
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取数据备份记录列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
