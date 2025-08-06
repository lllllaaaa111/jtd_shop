from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from .models import User, UserProfile, Address, Mine
from .serializers import UserSerializer, UserCreateSerializer, UserProfileSerializer
import logging
import json
import os
import uuid
from django.db import models

logger = logging.getLogger(__name__)

# 用户管理相关views
@api_view(['GET'])
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
