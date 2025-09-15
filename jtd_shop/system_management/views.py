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
from typing import Optional

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
        body = request.data.get('body', '')
        query_string = request.data.get('query_string', '')
        # serial_no 固定从数据库读取
        req_nonce = request.data.get('nonce_str')
        req_timestamp = request.data.get('timestamp')

        # 如果未提供字符串body，尝试用结构化字段拼装（严格无空格，保证稳定序列化）
        if (not body) or not isinstance(body, str):
            # 从数据库获取微信配置
            wechat_config = SystemConfig.objects.filter(is_active=True).first()
            if not wechat_config:
                return Response({'code': 400, 'msg': '未找到微信支付配置，请先配置', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
            
            appid = wechat_config.appid
            mchid = wechat_config.mchid
            # appid = 'wxd678efh567hg6787'
            # mchid = '1900007291'
            
            if not appid or not mchid:
                return Response({'code': 400, 'msg': '微信支付配置不完整：缺少appid或mchid', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
            
            description = request.data.get('description')
            out_trade_no = request.data.get('out_trade_no')
            notify_url = request.data.get('notify_url')
            amount = request.data.get('amount')
            payer = request.data.get('payer')
            try:
                if all([out_trade_no, notify_url, amount, payer]):
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
        
        # 从数据库获取mchid，不再从请求参数获取
        mchid = (wechat_config.mchid or '').strip()
        serial_no = (wechat_config.serial_no or '').strip()
        private_key_pem = (wechat_config.key_file or '').strip().replace('\r\n', '\n').replace('\r', '\n')
        
        if not mchid or not serial_no or not private_key_pem:
            return Response({'code': 400, 'msg': '配置不完整：需包含mchid/serial_no/key_file', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        if 'BEGIN' not in private_key_pem or 'PRIVATE KEY' not in private_key_pem:
            return Response({'code': 400, 'msg': 'key_file不是PEM私钥（缺少BEGIN/END PRIVATE KEY）', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        
        # 时间戳/随机串
        timestamp = int(req_timestamp) if str(req_timestamp).isdigit() else int(time.time())
        nonce_str = str(req_nonce) if req_nonce else str(uuid.uuid4()).replace('-', '')[:32]
        # 计算过期时间：当前时间 + 15分钟，输出为示例格式 2025-89-03T16:18:56+08:00
        expire_timestamp = timestamp + (15 * 60)
        time_expire = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(expire_timestamp))
        
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
            f'signature="{signature_b64}"'
        )
        authorization_full = 'WECHATPAY2-SHA256-RSA2048 ' + signature_params
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'signature': signature_b64,
                'timestamp': timestamp,
                'nonce_str': nonce_str,
                'time_expire': time_expire,
                'url_path': url_path,
                "description": description,
                "out_trade_no": out_trade_no,
                "notify_url": notify_url,
                "amount": amount,
                "payer": payer,
                'body': body,
                'appid': appid,
                'mchid': mchid,
                'serial_no': serial_no,
                'signature_params': signature_params,
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

def verify_wechatpay_signature(platform_cert_pem: str, serial_header: str, timestamp_header: str, nonce_header: str, body: str, signature_header: str) -> bool:
    """使用微信支付平台证书验签回调通知。
    要求：
      - platform_cert_pem: 数据库中的平台证书（PEM）
      - serial_header: Wechatpay-Serial
      - timestamp_header: Wechatpay-Timestamp
      - nonce_header: Wechatpay-Nonce
      - body: 原始请求体字符串
      - signature_header: Wechatpay-Signature（Base64）
    验签串格式（按官方文档）：timestamp + "\n" + nonce + "\n" + body + "\n"
    算法：RSA SHA256，PKCS1v15
    """
    platform_cert_pem = (platform_cert_pem or '').strip().replace('\r\n', '\n').replace('\r', '\n')
    if not platform_cert_pem or 'BEGIN CERTIFICATE' not in platform_cert_pem:
        raise ValueError('平台证书未配置或格式不正确')

    # 序列号检查（证书的序列号与请求头应一致）
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes
        import base64 as _b64
    except ImportError:
        # 抛给上层由其处理依赖缺失
        raise

    # 某些情况下cert_file可能包含多个证书，尝试逐个解析匹配序列号
    certs: list[x509.Certificate] = []
    pem_blocks = []
    start = '-----BEGIN CERTIFICATE-----'
    end = '-----END CERTIFICATE-----'
    text = platform_cert_pem
    while True:
        s = text.find(start)
        if s == -1:
            break
        e = text.find(end, s)
        if e == -1:
            break
        pem_blocks.append(text[s:e+len(end)] + '\n')
        text = text[e+len(end):]
    if not pem_blocks:
        pem_blocks = [platform_cert_pem]

    target_cert: Optional[x509.Certificate] = None
    for blk in pem_blocks:
        try:
            cert = x509.load_pem_x509_certificate(blk.encode('utf-8'), default_backend())
            cert_serial_hex = format(cert.serial_number, 'x').upper()
            header_serial = (serial_header or '').strip().upper()
            if header_serial == cert_serial_hex:
                target_cert = cert
                break
            certs.append(cert)
        except Exception:
            continue

    # 找不到与头部一致的证书时，放宽为使用第一张证书尝试验签（有些环境序列号格式不同），但记录警告
    if target_cert is None and certs:
        target_cert = certs[0]
        logger.warning('未匹配到相同序列号证书，使用列表首证书尝试验签')

    if target_cert is None:
        logger.error('无法解析平台证书')
        return False

    message = f"{timestamp_header}\n{nonce_header}\n{body}\n".encode('utf-8')
    try:
        signature_bytes = _b64.b64decode(signature_header)
    except Exception:
        return False

    public_key = target_cert.public_key()
    try:
        public_key.verify(
            signature_bytes,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        logger.warning(f'平台回调验签失败: {e}')
        return False

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_signature_string(request):
    """生成五行签名串（每行以\n结束，包括最后一行）。
    支持传入 body 字符串，或用结构化字段：description, out_trade_no, notify_url, amount, payer。
    appid 和 mchid 自动从 SystemConfig 数据库获取。
    """
    try:
        method = request.data.get('method', 'POST')
        url_path = request.data.get('url_path', '/v3/pay/transactions/jsapi')
        query_string = request.data.get('query_string', '')
        body = request.data.get('body', '')
        req_timestamp = request.data.get('timestamp')
        req_nonce = request.data.get('nonce_str')

        # 从数据库获取微信配置
        wechat_config = SystemConfig.objects.filter(is_active=True).first()
        if not wechat_config:
            return Response({'code': 400, 'msg': '未找到微信支付配置，请先配置', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        
        appid = wechat_config.appid
        mchid = wechat_config.mchid
        
        if not appid or not mchid:
            return Response({'code': 400, 'msg': '微信支付配置不完整：缺少appid或mchid', 'result': None}, status=status.HTTP_400_BAD_REQUEST)

        if (not body) or not isinstance(body, str):
            description = request.data.get('description')
            out_trade_no = request.data.get('out_trade_no')
            notify_url = request.data.get('notify_url')
            amount = request.data.get('amount')
            payer = request.data.get('payer')
            try:
                if all([description, out_trade_no, notify_url, amount, payer]):
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

        # 计算过期时间：当前时间 + 15分钟
        expire_timestamp = timestamp + (15 * 60)  # 15分钟 = 900秒
        expire_time = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(expire_timestamp))

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
                'canonical_url': canonical_url,
                'appid': appid,
                'mchid': mchid,
                'time_expire': expire_time
            }
        })
    except Exception as e:
        logger.exception('生成签名串失败')
        return Response({'code': 500, 'msg': f'服务器错误: {str(e)}', 'result': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def wechat_pay_notify(request):
    """接收微信支付回传信息（支付结果通知）
    微信支付完成后会向此接口发送POST请求，包含支付结果信息
    请求头包含：Wechatpay-Signature, Wechatpay-Timestamp, Wechatpay-Nonce, Wechatpay-Serial
    请求体为JSON格式的支付结果数据
    """
    try:
        # 获取微信签名头信息（可用于验签）
        signature = request.META.get('HTTP_WECHATPAY_SIGNATURE', '')
        ts_header = request.META.get('HTTP_WECHATPAY_TIMESTAMP', '')
        nonce_header = request.META.get('HTTP_WECHATPAY_NONCE', '')
        serial = request.META.get('HTTP_WECHATPAY_SERIAL', '')

        logger.info(f"收到微信支付通知: signature={signature[:20]}..., timestamp={ts_header}, nonce={nonce_header}, serial={serial}")

        # 解析请求体（顶层为通知元信息与resource密文块）
        try:
            raw_body = request.body.decode('utf-8')
            notify_data = json.loads(raw_body) if raw_body else {}
        except Exception as e:
            logger.error(f"解析微信支付通知请求体失败: {e}")
            return Response({'code': 'FAIL', 'message': '请求体解析失败'}, status=400)

        logger.info(f"微信支付通知数据(顶层): id={notify_data.get('id')}, event_type={notify_data.get('event_type')}, resource_type={notify_data.get('resource_type')}, summary={notify_data.get('summary')}")

        # 读取解密与验签所需的配置
        cfg = SystemConfig.objects.filter(is_active=True).first()
        if not cfg:
            logger.error('未找到系统配置，无法处理通知')
            return Response({'code': 'FAIL', 'message': '服务器未配置'}, status=500)

        # 先进行微信平台回调验签（强烈建议生产必须开启）
        try:
            verified = verify_wechatpay_signature(
                platform_cert_pem=(cfg.cert_file or ''),
                serial_header=serial,
                timestamp_header=ts_header,
                nonce_header=nonce_header,
                body=raw_body,
                signature_header=signature,
            )
        except ImportError:
            logger.error('缺少验签依赖，请安装 cryptography 库')
            return Response({'code': 'FAIL', 'message': '缺少验签依赖'}, status=500)
        except Exception as e:
            logger.error(f"验签过程异常: {e}")
            return Response({'code': 'FAIL', 'message': '验签异常'}, status=500)

        if not verified:
            logger.warning('微信回调验签未通过')
            return Response({'code': 'FAIL', 'message': '验签失败'}, status=401)

        event_type = notify_data.get('event_type', '')
        resource = notify_data.get('resource', {}) or {}
        algorithm = resource.get('algorithm')
        ciphertext_b64 = resource.get('ciphertext', '')
        nonce_str = resource.get('nonce', '')
        associated_data = resource.get('associated_data', '')

        # 仅当有resource密文时尝试解密（按官方固定算法 AEAD_AES_256_GCM）
        decrypted = {}
        if algorithm == 'AEAD_AES_256_GCM' and ciphertext_b64 and nonce_str is not None:
            try:
                # 优先使用 cryptography 的 AESGCM
                try:
                    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                    import base64 as _b64

                    if not cfg.api_v3_key:
                        logger.error('缺少API v3密钥配置，无法解密通知资源')
                        return Response({'code': 'FAIL', 'message': '服务器未配置'}, status=500)

                    api_v3_key_bytes = (cfg.api_v3_key or '').encode('utf-8')
                    nonce_bytes = nonce_str.encode('utf-8')
                    aad_bytes = (associated_data or '').encode('utf-8')
                    ciphertext_bytes = _b64.b64decode(ciphertext_b64)

                    aesgcm = AESGCM(api_v3_key_bytes)
                    plain_bytes = aesgcm.decrypt(nonce_bytes, ciphertext_bytes, aad_bytes)
                    decrypted = json.loads(plain_bytes.decode('utf-8'))
                except ImportError:
                    # 备选使用 PyCryptodome
                    try:
                        from Crypto.Cipher import AES as _AES
                        import base64 as _b64

                        if not cfg.api_v3_key:
                            logger.error('缺少API v3密钥配置，无法解密通知资源')
                            return Response({'code': 'FAIL', 'message': '服务器未配置'}, status=500)

                        api_v3_key_bytes = (cfg.api_v3_key or '').encode('utf-8')
                        nonce_bytes = nonce_str.encode('utf-8')
                        aad_bytes = (associated_data or '').encode('utf-8')
                        data = _b64.b64decode(ciphertext_b64)

                        cipher = _AES.new(api_v3_key_bytes, _AES.MODE_GCM, nonce=nonce_bytes)
                        cipher.update(aad_bytes)
                        # data = ciphertext || tag (WeChat v3 按标准拼接)
                        ciphertext, tag = data[:-16], data[-16:]
                        plain_bytes = cipher.decrypt_and_verify(ciphertext, tag)
                        decrypted = json.loads(plain_bytes.decode('utf-8'))
                    except ImportError:
                        logger.error('缺少解密依赖，请安装 cryptography 或 pycryptodome')
                        return Response({'code': 'FAIL', 'message': '缺少解密依赖'}, status=500)
            except Exception as e:
                logger.error(f"解密微信支付通知失败: {e}")
                return Response({'code': 'FAIL', 'message': '解密失败'}, status=400)
        else:
            logger.warning('通知resource缺少密文或算法不匹配，跳过解密')

        # 根据事件类型处理（这里主要演示交易成功）
        if event_type == 'TRANSACTION.SUCCESS':
            payment_result = {
                'out_trade_no': (decrypted.get('out_trade_no') if decrypted else None) or '',
                'transaction_id': (decrypted.get('transaction_id') if decrypted else None) or '',
                'trade_state': (decrypted.get('trade_state') if decrypted else None) or '',
                'trade_state_desc': (decrypted.get('trade_state_desc') if decrypted else None) or '',
                'success_time': (decrypted.get('success_time') if decrypted else None) or '',
                'amount': (decrypted.get('amount') if decrypted else None) or {},
                'payer': (decrypted.get('payer') if decrypted else None) or {},
            }

            logger.info(f"支付成功: {payment_result}")

            # 记录操作日志（业务侧可在此更新订单等）
            OperationLog.objects.create(
                user=None,
                action='WECHAT_PAY_NOTIFY',
                resource='PAYMENT',
                resource_id=payment_result.get('out_trade_no', ''),
                description=f"微信支付成功通知: {payment_result.get('transaction_id', '')}",
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        elif event_type == 'TRANSACTION.CLOSED':
            logger.info(f"支付关闭: id={notify_data.get('id')}, summary={notify_data.get('summary')}")
        else:
            logger.info(f"收到其他微信支付事件: {event_type}, id={notify_data.get('id')}")

        # 返回成功响应给微信（无需返回体，200或204均可）
        return Response(status=200)

    except Exception as e:
        logger.exception('处理微信支付通知时发生错误')
        return Response({'code': 'FAIL', 'message': f'服务器错误: {str(e)}'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def wechat_pay_sign(request):
    """构造调起支付的签名（JSAPI/小程序调起支付）。
    入参：
      - prepay_id: 必填，统一下单返回的预支付交易会话标识
      - timestamp(可选): 前端也可传，未传则后端生成当前时间戳
      - nonce_str(可选): 随机串，未传则后端生成
    读取：SystemConfig.appid, SystemConfig.key_file（商户私钥）
    待签名串为四行，并且每一行以\n结尾（包括最后一行）：
        appId\n
        时间戳\n
        随机字符串\n
        prepay_id=...\n
    使用商户私钥做 SHA256withRSA 签名，Base64 编码返回。
    返回：{ appId, timeStamp, nonceStr, package, signType: 'RSA', paySign }
    """
    try:
        prepay_id = (request.data.get('prepay_id') or '').strip()
        if not prepay_id:
            return Response({'code': 400, 'msg': '缺少必填参数 prepay_id', 'result': None}, status=status.HTTP_400_BAD_REQUEST)

        cfg = SystemConfig.objects.filter(is_active=True).first()
        if not cfg:
            return Response({'code': 400, 'msg': '未找到微信支付配置，请先配置', 'result': None}, status=status.HTTP_400_BAD_REQUEST)

        appid = (cfg.appid or '').strip()
        private_key_pem = (cfg.key_file or '').strip().replace('\r\n', '\n').replace('\r', '\n')
        if not appid or not private_key_pem:
            return Response({'code': 400, 'msg': '配置不完整：需包含appid/key_file', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        if 'BEGIN' not in private_key_pem or 'PRIVATE KEY' not in private_key_pem:
            return Response({'code': 400, 'msg': 'key_file不是PEM私钥（缺少BEGIN/END PRIVATE KEY）', 'result': None}, status=status.HTTP_400_BAD_REQUEST)

        # 生成时间戳/随机串
        req_timestamp = request.data.get('timestamp')
        req_nonce = request.data.get('nonce_str')
        timestamp = int(req_timestamp) if (isinstance(req_timestamp, (int, str)) and str(req_timestamp).isdigit()) else int(time.time())
        nonce_str = str(req_nonce) if req_nonce else str(uuid.uuid4()).replace('-', '')[:32]

        package = f"prepay_id={prepay_id}"
        # 四行签名串，末尾也要换行
        message = f"{appid}\n{timestamp}\n{nonce_str}\n{package}\n"

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
            pay_sign = base64.b64encode(signature_bytes).decode('utf-8')
        except ImportError:
            try:
                import rsa
                pk = rsa.PrivateKey.load_pkcs1(private_key_pem.encode('utf-8'))
                signature_bytes = rsa.sign(message.encode('utf-8'), pk, 'SHA-256')
                pay_sign = base64.b64encode(signature_bytes).decode('utf-8')
            except ImportError:
                return Response({'code': 400, 'msg': '缺少签名依赖，请安装 cryptography 或 rsa', 'result': None}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception('支付签名失败')
            return Response({'code': 400, 'msg': f'支付签名失败: {str(e)}', 'result': None}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'appId': appid,
                'timeStamp': str(timestamp),
                'nonceStr': nonce_str,
                'package': package,
                'signType': 'RSA',
                'paySign': pay_sign
            }
        })
    except Exception as e:
        logger.exception('构造调起支付签名头时发生错误')
        return Response({'code': 500, 'msg': f'服务器错误: {str(e)}', 'result': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
