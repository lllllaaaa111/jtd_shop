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
@permission_classes([AllowAny])  # 临时改为允许任何人访问，用于测试
def get_wechat_certificate(request):
    """生成微信支付签名头（按五行规范 + SHA256withRSA）。
    支持参数：
      - method, url_path, query_string
      - body: 字符串；或者提供结构化字段由服务端生成：
        appid, mchid, description, out_trade_no, notify_url,
        amount: { total, currency }, payer: { openid }
      - nonce_str(可选), timestamp(可选)
    返回：
      - signature_params: 不带算法前缀的签名参数串
      - authorization: 带算法前缀的完整Authorization
      - signature_string/message: 五行签名串（每行以\n）
    """
    try:
        method = request.data.get('method', 'POST')
        url_path = request.data.get('url_path', '/v3/pay/transactions/jsapi')
        query_string = request.data.get('query_string', '')
        body = request.data.get('body', '')
        # serial_no 固定从数据库读取
        req_nonce = request.data.get('nonce_str')
        req_timestamp = request.data.get('timestamp')

        # 如果未提供字符串body，尝试用结构化字段拼装（严格无空格，保证稳定序列化）
        if (not body) or not isinstance(body, str):
            appid = request.data.get('appid')
            mchid = request.data.get('mchid')
            description = request.data.get('description')
            out_trade_no = request.data.get('out_trade_no')
            notify_url = request.data.get('notify_url')
            amount = request.data.get('amount')
            payer = request.data.get('payer')
            try:
                if all([appid, mchid, description, out_trade_no, notify_url, amount, payer]):
                    body_obj = {
                        "appid": appid,
                        "mchid": mchid,
                        "description": description,
                        "out_trade_no": out_trade_no,
                        "notify_url": notify_url,
                        "amount": amount,
                        "payer": payer,
                    }
                    # 稳定序列化：无空格，使用ASCII保留原样字符转义
                    body = json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))
            except Exception:
                pass

        # 规范化 body 为字符串
        if body is None:
            body = ''
        elif not isinstance(body, str):
            try:
                body = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
            except Exception:
                body = str(body)

        # 读取微信配置
        wechat_config = SystemConfig.objects.filter(is_active=True).first()
        if not wechat_config:
            return Response({'code': 400, 'msg': '未找到微信支付配置，请先配置', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        
        mchid = (request.data.get('mchid') or '').strip()
        serial_no = (wechat_config.serial_no or '').strip()
        private_key_pem = (wechat_config.key_file or '').strip().replace('\r\n', '\n').replace('\r', '\n')
        
        if not mchid or not serial_no or not private_key_pem:
            return Response({'code': 400, 'msg': '配置不完整：需包含mchid/serial_no/key_file', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        if 'BEGIN' not in private_key_pem or 'PRIVATE KEY' not in private_key_pem:
            return Response({'code': 400, 'msg': 'key_file不是PEM私钥（缺少BEGIN/END PRIVATE KEY）', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # 时间戳/随机串
        timestamp = int(req_timestamp) if str(req_timestamp).isdigit() else int(time.time())
        nonce_str = str(req_nonce) if req_nonce else str(uuid.uuid4()).replace('-', '')[:32]
        
        # 构建canonical URL
        canonical_url = url_path or '/'
        if query_string:
            canonical_url += '?' + query_string
        
        # 五行待签名串
        message = build_message_rsa(method, canonical_url, timestamp, nonce_str, body)
        
        # 签名：SHA256withRSA(Base64)
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.backends import default_backend

            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            signature_bytes = private_key.sign(
                message.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        except ImportError:
            try:
                import rsa
                pk = rsa.PrivateKey.load_pkcs1(private_key_pem.encode('utf-8'))
                signature_bytes = rsa.sign(message.encode('utf-8'), pk, 'SHA-256')
                signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            except ImportError:
                return Response({'code': 400, 'msg': '缺少签名依赖，请安装 cryptography 或 rsa', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception('签名失败')
            return Response({'code': 400, 'msg': f'签名失败: {str(e)}', 'result': None}, status=status.HTTP_400_BAD_REQUEST)

        signature_params = (
            f'mchid="{mchid}",' \
            f'nonce_str="{nonce_str}",' \
            f'timestamp="{timestamp}",' \
            f'serial_no="{serial_no}",' \
            f'signature="{signature_b64}"'
        )
        authorization_full = 'WECHATPAY2-SHA256-RSA2048 ' + signature_params
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'signature_params': signature_params,
                'authorization': authorization_full,
                'timestamp': timestamp,
                'nonce_str': nonce_str,
                'serial_no': serial_no,
                'mchid': mchid,
                'signature': signature_b64,
                'signature_string': message,
                'message': message,
                'canonical_url': canonical_url,
                'body': body
            }
        })

    except Exception as e:
        logger.exception("生成微信支付签名头时发生错误")
        try:
            import traceback
            trace = traceback.format_exc()
        except Exception:
            trace = ''
        return Response({'code': 500, 'msg': f'服务器错误: {str(e)}', 'trace': trace, 'result': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_signature_string(request):
    """生成五行签名串（每行以\n结束，包括最后一行）。
    支持传入 body 字符串，或用结构化字段：appid, mchid, description, out_trade_no, notify_url, amount, payer。
    """
    try:
        method = request.data.get('method', 'POST')
        url_path = request.data.get('url_path', '/v3/pay/transactions/jsapi')
        query_string = request.data.get('query_string', '')
        body = request.data.get('body', '')
        req_timestamp = request.data.get('timestamp')
        req_nonce = request.data.get('nonce_str')

        if (not body) or not isinstance(body, str):
            appid = request.data.get('appid')
            mchid = request.data.get('mchid')
            description = request.data.get('description')
            out_trade_no = request.data.get('out_trade_no')
            notify_url = request.data.get('notify_url')
            amount = request.data.get('amount')
            payer = request.data.get('payer')
            try:
                if all([appid, mchid, description, out_trade_no, notify_url, amount, payer]):
                    body_obj = {
                        "appid": appid,
                        "mchid": mchid,
                        "description": description,
                        "out_trade_no": out_trade_no,
                        "notify_url": notify_url,
                        "amount": amount,
                        "payer": payer,
                    }
                    body = json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))
            except Exception:
                pass

        if body is None:
            body = ''
        elif not isinstance(body, str):
            try:
                body = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
            except Exception:
                body = str(body)

        timestamp = int(req_timestamp) if str(req_timestamp).isdigit() else int(time.time())
        nonce_str = str(req_nonce) if req_nonce else str(uuid.uuid4()).replace('-', '')[:32]

        canonical_url = url_path or '/'
        if query_string:
            canonical_url += '?' + query_string

        signature_string = build_message_rsa(method, canonical_url, timestamp, nonce_str, body)

        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'signature_string': signature_string,
                'method': method,
                'url_path': url_path,
                'query_string': query_string,
                'timestamp': timestamp,
                'nonce_str': nonce_str,
                'body': body,
                'canonical_url': canonical_url
            }
        })
    except Exception as e:
        logger.exception('生成签名串失败')
        return Response({'code': 500, 'msg': f'服务器错误: {str(e)}', 'result': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
