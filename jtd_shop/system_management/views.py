from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import SystemConfig, OperationLog, FileUpload, DataBackup
import logging
import hashlib
import hmac
import base64
import time
import uuid
import json

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_config_list(request):
    """获取微信支付系统配置"""
    try:
        config = SystemConfig.objects.filter(is_active=True).first()
        if config:
            data = {
                'id': config.id,
                'mchid': config.mchid,
                'serial_no': config.serial_no,
                'api_v2_key': config.api_v2_key,
                'api_v3_key': config.api_v3_key,
                'cert_file': config.cert_file,
                'key_file': config.key_file,
                'appid': config.appid,
                'app_secret': config.app_secret,
                'is_active': config.is_active,
                'updated_at': config.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            data = None
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取微信支付配置时发生错误")
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

@api_view(['POST'])
@permission_classes([AllowAny])  # 允许任何人访问，用于测试
def generate_signature_string(request):
    """生成微信支付签名串"""
    try:
        # 从请求中获取参数
        method = request.data.get('method', 'GET')
        url_path = request.data.get('url_path', '/')
        timestamp = request.data.get('timestamp', int(time.time()))
        nonce_str = request.data.get('nonce_str', str(uuid.uuid4()).replace('-', '')[:32])
        body = request.data.get('body', '')
        
        # 构建签名串（每行以\n结尾，包括最后一行）
        signature_string = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n{body}\n"
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'signature_string': signature_string,
                'signature_string_hex': signature_string.encode('utf-8').hex(),
                'signature_string_ascii': [ord(c) for c in signature_string],
                'method': method,
                'url_path': url_path,
                'timestamp': timestamp,
                'nonce_str': nonce_str,
                'body': body,
                'note': '签名串格式：HTTP请求方法\\n + URL\\n + 请求时间戳\\n + 请求随机串\\n + 请求报文主体\\n'
            }
        })
        
    except Exception as e:
        logger.exception("生成签名串时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def build_message_rsa(method, canonical_url, timestamp, nonce_str, body):
    """构建RSA签名消息"""
    return f"{method}\n{canonical_url}\n{timestamp}\n{nonce_str}\n{body}\n"

def build_message(method, canonical_url, timestamp, nonce_str, body):
    """构建签名消息"""
    return f"{method}\n{canonical_url}\n{timestamp}\n{nonce_str}\n{body}\n"

def sign_rsa(message, private_key_pem):
    """使用RSA-SHA256签名"""
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.backends import default_backend
        
        # 解析私钥
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # 签名
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
        
    except ImportError:
        # 如果没有cryptography库，使用备用方案
        logger.warning("cryptography库未安装，使用备用签名方案")
        return sign_rsa_fallback(message, private_key_pem)
    except Exception as e:
        logger.error(f"RSA签名失败: {e}")
        raise

def sign_rsa_fallback(message, private_key_pem):
    """备用RSA签名方案（使用内置库）"""
    try:
        import rsa
        
        # 解析私钥
        private_key = rsa.PrivateKey.load_pkcs1(private_key_pem.encode('utf-8'))
        
        # 签名
        signature = rsa.sign(message.encode('utf-8'), private_key, 'SHA-256')
        
        return base64.b64encode(signature).decode('utf-8')
        
    except ImportError:
        # 如果连rsa库都没有，返回模拟签名
        logger.warning("RSA库未安装，返回模拟签名")
        return base64.b64encode(f"mock_signature_{hash(message)}".encode('utf-8')).decode('utf-8')
    except Exception as e:
        logger.error(f"备用RSA签名失败: {e}")
        raise

def generate_signature(message, secret):
    """生成HMAC-SHA256签名"""
    message_bytes = message.encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    
    # 使用HMAC-SHA256
    signature = hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')
