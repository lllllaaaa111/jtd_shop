from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from .models import User, UserProfile, Address, Mine
from .serializers import UserSerializer, UserCreateSerializer, UserProfileSerializer
import logging
import json
import os
import uuid
from django.db import models
import base64

try:
    from Crypto.Cipher import AES
except Exception:  # noqa: E722
    AES = None

logger = logging.getLogger(__name__)

# CSRF认证相关接口
@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """获取CSRF令牌"""
    try:
        # 获取CSRF令牌
        csrf_token = get_token(request)
        
        return Response({
            'code': 200,
            'msg': '获取CSRF令牌成功',
            'result': {
                'csrf_token': csrf_token,
                'token_length': len(csrf_token),
                'expires_in': 'session',  # CSRF令牌在session期间有效
                'usage': '在POST请求头中使用 X-CSRFToken 或 X-Csrftoken'
            }
        })
    except Exception as e:
        logger.exception("获取CSRF令牌失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_csrf_token(request):
    """验证CSRF令牌"""
    try:
        # 从请求头获取CSRF令牌
        csrf_token = request.headers.get('X-CSRFToken') or request.headers.get('X-Csrftoken')
        
        if not csrf_token:
            return Response({
                'code': 400,
                'msg': '缺少CSRF令牌',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证CSRF令牌
        from django.middleware.csrf import CsrfViewMiddleware
        from django.test import RequestFactory
        
        # 创建一个临时的请求工厂来验证令牌
        factory = RequestFactory()
        temp_request = factory.post('/')
        temp_request.META['CSRF_COOKIE'] = request.META.get('CSRF_COOKIE')
        
        middleware = CsrfViewMiddleware(lambda req: None)
        
        try:
            # 验证令牌
            middleware.process_view(temp_request, None, (), {})
            return Response({
                'code': 200,
                'msg': 'CSRF令牌验证成功',
                'result': {
                    'valid': True,
                    'token_length': len(csrf_token)
                }
            })
        except Exception:
            return Response({
                'code': 400,
                'msg': 'CSRF令牌无效',
                'result': {
                    'valid': False,
                    'token_length': len(csrf_token)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.exception("验证CSRF令牌失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_info(request):
    """获取CSRF相关信息"""
    try:
        # 获取当前CSRF令牌
        csrf_token = get_token(request)
        
        # 获取CSRF配置信息
        from django.conf import settings
        
        csrf_info = {
            'csrf_token': csrf_token,
            'token_length': len(csrf_token),
            'cookie_name': getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken'),
            'header_name': getattr(settings, 'CSRF_HEADER_NAME', 'HTTP_X_CSRFTOKEN'),
            'cookie_age': getattr(settings, 'CSRF_COOKIE_AGE', 31449600),
            'cookie_secure': getattr(settings, 'CSRF_COOKIE_SECURE', False),
            'cookie_httponly': getattr(settings, 'CSRF_COOKIE_HTTPONLY', False),
            'usage_instructions': {
                'get_token': 'GET /users/csrf/token/',
                'validate_token': 'POST /users/csrf/validate/',
                'request_header': 'X-CSRFToken 或 X-Csrftoken',
                'example': 'X-CSRFToken: your_csrf_token_here'
            }
        }
        
        return Response({
            'code': 200,
            'msg': '获取CSRF信息成功',
            'result': csrf_info
        })
    except Exception as e:
        logger.exception("获取CSRF信息失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 认证相关接口
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """用户登录"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'code': 400,
                'msg': '用户名和密码不能为空',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'code': 200,
                'msg': '登录成功',
                'result': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff
                }
            })
        else:
            return Response({
                'code': 401,
                'msg': '用户名或密码错误',
                'result': None
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.exception("用户登录失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    """用户注册"""
    try:
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 自动登录
            login(request, user)
            return Response({
                'code': 201,
                'msg': '注册成功',
                'result': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'code': 400,
                'msg': '注册参数错误',
                'result': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("用户注册失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def user_logout(request):
    """用户登出"""
    try:
        logout(request)
        return Response({
            'code': 200,
            'msg': '登出成功',
            'result': None
        })
    except Exception as e:
        logger.exception("用户登出失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_info(request):
    """获取当前用户信息"""
    try:
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response({
                'code': 200,
                'msg': 'success',
                'result': serializer.data
            })
        else:
            return Response({
                'code': 401,
                'msg': '用户未登录',
                'result': None
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.exception("获取用户信息失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 用户管理相关views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """获取用户列表"""
    try:
        users = User.objects.filter(is_active=True)
        serializer = UserSerializer(users, many=True)
        return Response({
            'code': 200,
            'msg': 'success',
            'result': serializer.data
        })
    except Exception as e:
        logger.exception("获取用户列表失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """获取用户详情"""
    try:
        user = get_object_or_404(User, id=user_id, is_active=True)
        serializer = UserSerializer(user)
        return Response({
            'code': 200,
            'msg': 'success',
            'result': serializer.data
        })
    except Exception as e:
        logger.exception(f"获取用户详情失败: {user_id}")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_create(request):
    """创建新用户"""
    try:
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'code': 201,
                'msg': '用户创建成功',
                'result': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'code': 400,
                'msg': '参数错误',
                'result': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("创建用户失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def user_update(request, user_id):
    """更新用户信息"""
    try:
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'msg': '用户信息更新成功',
                'result': serializer.data
            })
        else:
            return Response({
                'code': 400,
                'msg': '参数错误',
                'result': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"更新用户信息失败: {user_id}")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def user_delete(request, user_id):
    """删除用户（软删除）"""
    try:
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()
        return Response({
            'code': 200,
            'msg': '用户删除成功',
            'result': {'deleted_id': user_id}
        })
    except Exception as e:
        logger.exception(f"删除用户失败: {user_id}")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 头像管理相关views
def get_user_mine(request):
    """获取用户的头像图片"""
    try:
        # 获取最新的 Mine 图片
        mine_image = Mine.objects.filter(
            is_delete=False
        ).order_by('-order', '-created_at').first()

        if not mine_image:
            return JsonResponse({
                'code': 404,
                'msg': '未找到头像图片',
                'result': None
            })

        # 构建完整的 URL
        image_url = request.build_absolute_uri(mine_image.img.url)

        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'result': {
                'id': mine_image.id,
                'image_url': image_url,
                'name': mine_image.name or '未命名',
                'order': mine_image.order,
                'created_at': mine_image.created_at.strftime("%Y-%m-%d")
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

def mine_image_list(request):
    """获取用户头像图片列表"""
    try:
        images = Mine.objects.filter(is_delete=False).order_by('order', '-created_at')

        data = []
        for img in images:
            data.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.img.url),
                'name': img.name or '未命名',
                'order': img.order,
                'created_at': img.created_at.strftime("%Y-%m-%d")
            })

        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

@csrf_exempt
def upload_mine_image(request):
    """处理头像图片上传"""
    if request.method == 'POST' and request.FILES.get('image'):
        # 获取上传的文件
        image_file = request.FILES['image']

        # 验证文件类型
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(image_file.name)[1].lower()

        if file_ext not in allowed_extensions:
            return JsonResponse({
                'code': 400,
                'msg': f'不支持的文件类型: {file_ext}'
            })

        # 验证文件大小（最大5MB）
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'code': 400,
                'msg': '文件大小不能超过5MB'
            })

        try:
            # 创建新的 Mine 记录
            mine_image = Mine()

            # 设置初始名称
            mine_image.name = f"头像 {timezone.now().strftime('%Y-%m-%d')}"

            # 生成唯一文件名
            new_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join('mine', new_filename)

            # 保存文件
            saved_path = default_storage.save(file_path, image_file)
            mine_image.img = saved_path

            # 获取最新的 order 值
            max_order = Mine.objects.aggregate(models.Max('order')).get('order__max', 0) or 0
            mine_image.order = max_order + 1

            # 保存到数据库
            mine_image.save()

            # 构建完整的 URL
            full_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)

            return JsonResponse({
                'code': 200,
                'msg': '图片上传成功',
                'result': {
                    'id': mine_image.id,
                    'image_url': full_url,
                    'name': mine_image.name,
                    'order': mine_image.order
                }
            })
        except Exception as e:
            # 如果发生错误，删除已保存的文件
            if 'saved_path' in locals():
                default_storage.delete(saved_path)
            return JsonResponse({
                'code': 500,
                'msg': f'上传失败: {str(e)}'
            })

    return JsonResponse({
        'code': 400,
        'msg': '无效请求或未上传图片'
    })

@csrf_exempt
def delete_mine_image(request):
    """删除 Mine 图片"""
    logger.info(f"收到请求: {request.method} {request.path}")

    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        logger.info("处理OPTIONS预检请求")
        response = HttpResponse(status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        return response

    # 处理 POST 请求
    if request.method == 'POST':
        logger.info("处理POST请求")
        logger.info(f"请求头: {request.headers}")
        logger.info(f"请求体: {request.body}")

        try:
            # 尝试解析 JSON 数据
            try:
                data = json.loads(request.body)
                image_id = data.get('image_id')
                logger.info(f"从JSON获取image_id: {image_id}")
            except Exception as json_err:
                logger.warning(f"JSON解析失败: {str(json_err)}")
                # 尝试从表单数据获取
                image_id = request.POST.get('image_id')
                logger.info(f"从表单获取image_id: {image_id}")

            if not image_id:
                logger.error("缺少图片ID参数")
                return HttpResponse(
                    json.dumps({
                        'code': 400,
                        'msg': '缺少图片ID参数'
                    }),
                    content_type='application/json',
                    status=400
                )

            # 查找图片记录
            try:
                mine_image = Mine.objects.get(id=image_id)
                logger.info(f"找到图片: {mine_image.name}")

                # 删除物理文件
                if mine_image.img:
                    if default_storage.exists(mine_image.img.name):
                        default_storage.delete(mine_image.img.name)
                        logger.info(f"已删除物理文件: {mine_image.img.name}")

                # 删除数据库记录
                mine_image.delete()
                logger.info(f"已删除数据库记录: {image_id}")

            except Mine.DoesNotExist:
                logger.error(f"未找到图片ID: {image_id}")
                return HttpResponse(
                    json.dumps({
                        'code': 404,
                        'msg': '未找到指定图片'
                    }),
                    content_type='application/json',
                    status=404
                )

            # 返回成功响应
            response_data = {
                'code': 200,
                'msg': '图片删除成功',
                'deleted_id': image_id
            }
            logger.info(f"返回成功响应: {response_data}")
            return HttpResponse(
                json.dumps(response_data),
                content_type='application/json',
                status=200
            )

        except Exception as e:
            logger.exception(f"删除图片时发生错误: {str(e)}")
            return HttpResponse(
                json.dumps({
                    'code': 500,
                    'msg': f'删除失败: {str(e)}'
                }),
                content_type='application/json',
                status=500
            )

    # 处理其他请求方法
    logger.warning(f"不支持的请求方法: {request.method}")
    return HttpResponse(
        json.dumps({
            'code': 405,
            'msg': f'不支持的请求方法: {request.method}'
        }),
        content_type='application/json',
        status=405
    )

@csrf_exempt
def set_mine_avatar(request):
    """设置用户的当前头像"""
    logger.info(f"收到请求: {request.method} {request.path}")

    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        logger.info("处理OPTIONS预检请求")
        response = JsonResponse({}, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        return response

    # 处理 POST 请求
    if request.method == 'POST':
        logger.info("处理POST请求")
        logger.info(f"请求头: {request.headers}")
        logger.info(f"请求体: {request.body}")

        try:
            # 尝试解析 JSON 数据
            try:
                data = json.loads(request.body)
                image_id = data.get('image_id')
                logger.info(f"从JSON获取image_id: {image_id}")
            except Exception as json_err:
                logger.warning(f"JSON解析失败: {str(json_err)}")
                # 尝试从表单数据获取
                image_id = request.POST.get('image_id')
                logger.info(f"从表单获取image_id: {image_id}")

            if not image_id:
                logger.error("缺少图片ID参数")
                return JsonResponse({
                    'code': 400,
                    'msg': '缺少图片ID参数'
                })

            # 查找图片记录
            try:
                mine_image = Mine.objects.get(id=image_id)
                logger.info(f"找到图片: {mine_image.name}")
            except Mine.DoesNotExist:
                logger.error(f"未找到图片ID: {image_id}")
                return JsonResponse({
                    'code': 404,
                    'msg': '未找到指定图片'
                })

            # 返回成功响应
            response_data = {
                'code': 200,
                'msg': '头像设置成功',
                'result': {
                    'id': mine_image.id,
                    'image_url': request.build_absolute_uri(mine_image.img.url),
                    'name': mine_image.name
                }
            }
            logger.info(f"返回成功响应: {response_data}")
            return JsonResponse(response_data)

        except Exception as e:
            logger.exception("设置头像时发生错误")
            return JsonResponse({
                'code': 500,
                'msg': f'设置失败: {str(e)}'
            })

    # 处理其他请求方法
    logger.warning(f"不支持的请求方法: {request.method}")
    return JsonResponse({
        'code': 405,
        'msg': f'不支持的请求方法: {request.method}'
    }, status=405)

@api_view(['POST'])
@permission_classes([AllowAny])
def aes_phone(request):
    """
    AES-CBC(PKCS7) 解密用户手机号
    支持AES-128(16字节key)和AES-192(24字节key)
    请求JSON参数: { "key": base64字符串, "encryptedDatastr": base64字符串, "iv": base64字符串 }
    返回: { code, msg, result: { phone_number } }
    注: 需要客户端携带CSRF（POST）
    """
    try:
        if AES is None:
            return Response({
                'code': 500,
                'msg': '服务器未安装AES库，请安装 pycryptodome',
                'result': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = request.data if isinstance(request.data, dict) else {}
        key_b64 = data.get('key')
        enc_b64 = data.get('encryptedDatastr')
        iv_b64 = data.get('iv')
        
        if not key_b64 or not enc_b64 or not iv_b64:
            return Response({
                'code': 400,
                'msg': '缺少必填参数: key / encryptedDatastr / iv',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base64解码
        try:
            key = base64.b64decode(key_b64)
            iv = base64.b64decode(iv_b64)
            cipher_data = base64.b64decode(enc_b64)
            logger.info(f"Base64解码成功 - Key长度: {len(key)}, IV长度: {len(iv)}, 密文长度: {len(cipher_data)}")
        except Exception as e:
            logger.error(f"Base64解码失败: {e}")
            return Response({
                'code': 400,
                'msg': 'Base64解码失败，请检查参数格式',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 长度校验 - 支持AES-128和AES-192
        if len(key) not in (16, 24):
            return Response({
                'code': 400,
                'msg': f'key长度必须为16字节（AES-128）或24字节（AES-192），实际{len(key)}字节',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if len(iv) != 16:
            return Response({
                'code': 400,
                'msg': f'iv长度必须为16字节，实际{len(iv)}字节',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if len(cipher_data) == 0 or (len(cipher_data) % 16) != 0:
            return Response({
                'code': 400,
                'msg': f'密文长度必须为16的整数倍，实际{len(cipher_data)}字节',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # AES-CBC解密
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(cipher_data)
            logger.info(f"AES-CBC解密成功，解密后数据长度: {len(decrypted)}")
            logger.info(f"解密后数据末尾字节: {[b for b in decrypted[-16:]]}")
        except Exception as e:
            logger.exception("AES-CBC解密失败")
            return Response({
                'code': 400,
                'msg': f'AES解密失败：{str(e)}',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # PKCS7去填充 - 改进版本
        try:
            plaintext = None
            
            # 方式1: 标准PKCS7去填充
            try:
                pad_len = decrypted[-1]
                if isinstance(pad_len, str):
                    pad_len = ord(pad_len)
                
                logger.info(f"检测到填充长度: {pad_len}")
                
                # 验证填充的有效性
                if 1 <= pad_len <= 16:
                    # 验证填充内容
                    padding = decrypted[-pad_len:]
                    logger.info(f"填充内容: {[b for b in padding]}")
                    
                    if all(b == pad_len for b in padding):
                        plaintext = decrypted[:-pad_len]
                        logger.info(f"标准PKCS7去填充成功，填充长度: {pad_len}")
                    else:
                        logger.warning("PKCS7填充内容验证失败")
                else:
                    logger.warning(f"填充长度超出范围: {pad_len}")
            except Exception as e:
                logger.warning(f"标准PKCS7去填充失败: {e}")
            
            # 方式2: 如果标准PKCS7失败，尝试其他方法
            if plaintext is None:
                logger.info("尝试其他去填充方法...")
                
                # 检查是否以JSON结尾字符结束
                if decrypted.endswith(b'}') or decrypted.endswith(b']') or decrypted.endswith(b'"'):
                    plaintext = decrypted
                    logger.info("使用无填充模式（数据以有效JSON结尾）")
                else:
                    # 尝试去除零填充
                    plaintext = decrypted.rstrip(b'\x00')
                    if len(plaintext) < len(decrypted):
                        logger.info(f"去除零填充，长度从{len(decrypted)}变为{len(plaintext)}")
                    else:
                        # 如果还是失败，尝试去除末尾的无效字节
                        # 寻找可能的JSON结束位置
                        for i in range(len(decrypted) - 1, max(0, len(decrypted) - 20), -1):
                            if decrypted[i] in [b'}', b']', b'"']:
                                plaintext = decrypted[:i+1]
                                logger.info(f"通过查找JSON结束符去填充，长度: {len(plaintext)}")
                                break
                        else:
                            plaintext = decrypted
                            logger.info("使用原始解密数据")
            
            if plaintext is None or len(plaintext) == 0:
                return Response({
                    'code': 400,
                    'msg': '解密后数据为空',
                    'result': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
            logger.info(f"最终明文长度: {len(plaintext)}")
            logger.info(f"明文数据(hex): {plaintext.hex()}")
                
        except Exception as e:
            logger.exception("去填充处理失败")
            return Response({
                'code': 400,
                'msg': f'去填充失败: {str(e)}',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 解析JSON
        try:
            # 尝试UTF-8解码
            try:
                text = plaintext.decode('utf-8')
                logger.info(f"UTF-8解码成功: {repr(text)}")
            except UnicodeDecodeError as e:
                logger.warning(f"UTF-8解码失败: {e}")
                # 尝试其他编码
                try:
                    text = plaintext.decode('latin-1')
                    logger.info(f"Latin-1解码成功: {repr(text)}")
                except Exception:
                    # 如果都失败，尝试忽略错误
                    text = plaintext.decode('utf-8', errors='ignore')
                    logger.info(f"UTF-8忽略错误解码: {repr(text)}")
            
            payload = json.loads(text)
            logger.info(f"JSON解析成功: {payload}")
        except Exception as e:
            logger.exception("JSON解析失败")
            return Response({
                'code': 400,
                'msg': f'JSON解析失败: {str(e)}',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 提取手机号
        phone = payload.get('phoneNumber') or payload.get('purePhoneNumber') or payload.get('phone')
        if not phone:
            return Response({
                'code': 404,
                'msg': '未在解密数据中找到手机号字段',
                'result': {'raw': payload}
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'code': 200,
            'msg': '解密成功',
            'result': {
                'phone_number': phone
            }
        })
        
    except Exception as e:
        logger.exception('AES解密失败')
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------- 地址管理相关接口 --------------------
from .serializers import AddressSerializer, AddressCreateSerializer, AddressUpdateSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def address_list(request):
    """查询用户地址列表（默认当前用户，可通过?user_id= 指定）"""
    try:
        user_id = request.query_params.get('user_id')
        if user_id:
            target_user = get_object_or_404(User, id=user_id)
        else:
            target_user = request.user
        
        if (not request.user.is_staff) and (target_user != request.user):
            return Response({
                'code': 403,
                'msg': '无权限查看其他用户地址',
                'result': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        addresses = Address.objects.filter(user=target_user).order_by('-is_default', 'id')
        serializer = AddressSerializer(addresses, many=True)
        return Response({
            'code': 200,
            'msg': 'success',
            'result': serializer.data
        })
    except Exception as e:
        logger.exception("获取地址列表失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def address_detail(request, address_id):
    """查询单个地址详情"""
    try:
        address = get_object_or_404(Address, id=address_id)
        if (not request.user.is_staff) and (address.user != request.user):
            return Response({
                'code': 403,
                'msg': '无权限查看该地址',
                'result': None
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = AddressSerializer(address)
        return Response({
            'code': 200,
            'msg': 'success',
            'result': serializer.data
        })
    except Exception as e:
        logger.exception("获取地址详情失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def address_create(request):
    """添加用户地址。若is_default为True，则取消该用户其他默认地址"""
    try:
        data = request.data.copy()
        if not data.get('user'):
            data['user'] = request.user.id
        serializer = AddressCreateSerializer(data=data)
        if serializer.is_valid():
            address = serializer.save()
            # 处理默认地址唯一性
            if address.is_default:
                Address.objects.filter(user=address.user).exclude(id=address.id).update(is_default=False)
            return Response({
                'code': 201,
                'msg': '地址添加成功',
                'result': AddressSerializer(address).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'code': 400,
                'msg': '参数错误',
                'result': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("添加地址失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def address_update(request, address_id):
    """修改用户地址。若is_default为True，则取消该用户其他默认地址"""
    try:
        address = get_object_or_404(Address, id=address_id)
        if (not request.user.is_staff) and (address.user != request.user):
            return Response({
                'code': 403,
                'msg': '无权限修改该地址',
                'result': None
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = AddressUpdateSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            if serializer.validated_data.get('is_default') is True:
                Address.objects.filter(user=updated.user).exclude(id=updated.id).update(is_default=False)
            return Response({
                'code': 200,
                'msg': '地址更新成功',
                'result': AddressSerializer(updated).data
            })
        else:
            return Response({
                'code': 400,
                'msg': '参数错误',
                'result': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("更新地址失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def address_delete(request, address_id):
    """删除用户地址"""
    try:
        address = get_object_or_404(Address, id=address_id)
        if (not request.user.is_staff) and (address.user != request.user):
            return Response({
                'code': 403,
                'msg': '无权限删除该地址',
                'result': None
            }, status=status.HTTP_403_FORBIDDEN)
        address.delete()
        return Response({
            'code': 200,
            'msg': '地址删除成功',
            'result': {'deleted_id': address_id}
        })
    except Exception as e:
        logger.exception("删除地址失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
