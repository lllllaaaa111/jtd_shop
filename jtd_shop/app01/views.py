import json
import random
import time

from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
# views.py
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import uuid
from .models import Welcome, Mine
from django.db import models
import logging

logger = logging.getLogger(__name__)

def index(request):
    time.sleep(0.2)
    return JsonResponse({"product_name":"油滋滋汉堡","product_price":"16元","description":"汉堡赛高！"})


def films(request):
    with open('./films.json', 'r', encoding='utf-8') as f:
        dic = json.load(f)
    return JsonResponse(dic)

def random_t_views(request):
    ii=[]
    for i in range(3):
        ii.append(random.randint(1,99999999))
    return JsonResponse(ii,safe=False)#数据里面有列表只能设置safe=false了


def welcome(request):
    """获取 Welcome 图片"""
    try:
        # 获取最新的 Welcome 图片
        welcome_image = Welcome.objects.filter(
            is_delete=False
        ).order_by('-order').first()  # 使用 first() 而不是 get()

        if not welcome_image:
            logger.warning("未找到 Welcome 图片")
            return JsonResponse({
                'code': 404,
                'msg': '未找到欢迎图片',
                'result': None
            })

        # 构建图片 URL
        image_url = request.build_absolute_uri(welcome_image.img.url)

        return JsonResponse({
            'code': 100,
            'msg': 'success',
            'result': {
                'id': str(welcome_image.id),
                'image_url': image_url,
                'order': welcome_image.order,
                'created_at': welcome_image.created_at.strftime("%Y-%m-%d")
            }
        })
    except Exception as e:
        logger.exception("处理 /smart/welcome/ 请求时发生错误")
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })


def welcome_image_list(request):
    """获取 Welcome 图片列表"""
    try:
        # 获取所有未被删除的 Welcome 图片，按 order 排序
        images = Welcome.objects.filter(is_delete=False).order_by('order')

        # 如果没有图片，返回默认图片
        if not images.exists():
            logger.warning("数据库中没有 Welcome 图片记录")
            return JsonResponse({
                'code': 100,
                'msg': 'success',
                'result': [{
                    'image_url': request.build_absolute_uri(settings.STATIC_URL + 'images/default_welcome.jpg'),
                    'order': 0,
                    'created_at': '2025-07-15'
                }]
            })

        # 构建响应数据
        data = []
        for img in images:
            try:
                # 构建完整的图片 URL
                image_url = request.build_absolute_uri(img.img.url)
            except Exception as e:
                logger.error(f"构建图片 URL 失败: {str(e)}")
                # 使用默认图片
                image_url = request.build_absolute_uri(settings.STATIC_URL + 'images/default_welcome.jpg')

            data.append({
                'image_url': image_url,
                'order': img.order,
                'created_at': img.create_time.strftime("%Y-%m-%d")
            })

        return JsonResponse({
            'code': 100,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("处理 /smart/welcome/ 请求时发生错误")
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

def mine(request):
    pass
    # 获取最新的 Mine 图片
    mine_obj = Mine.objects.filter(is_delete=False).order_by('-order').first()
    # 构建响应数据 - 添加格式参数
    result = {
        'original_url': request.build_absolute_uri(mine_obj.img.url) if mine_obj else settings.DEFAULT_MINE_IMAGE_URL,
        'formats': {
            # 添加不同格式的图片URL（这里使用简单的后缀方式，实际生产中可以使用图片处理库）
            'thumbnail': f"{request.build_absolute_uri(mine_obj.img.url)}?format=thumb&size=150x150",
            'large': f"{request.build_absolute_uri(mine_obj.img.url)}?format=large&size=600x600",
            'webp': f"{request.build_absolute_uri(mine_obj.img.url)}?format=webp"
        }
    }

    return JsonResponse({
        'code': 100,
        'msg': 'success',
        'result': result
    })


# app01/views.py
def welcome_image_list(request):
    """获取 Welcome 图片列表"""
    try:
        images = Welcome.objects.filter(is_delete=False).order_by('order')

        data = []
        for img in images:
            data.append({
                'id': img.id,  # 整数 ID
                'image_url': request.build_absolute_uri(img.img.url),
                'order': img.order,
                'created_at': img.created_at.strftime("%Y-%m-%d")
            })

        return JsonResponse({
            'code': 100,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

def mine_image_list(request):
    """获取 Welcome 图片列表"""
    try:
        images = Mine.objects.filter(is_delete=False).order_by('order')

        data = []
        for img in images:
            data.append({
                'id': img.id,  # 整数 ID
                'image_url': request.build_absolute_uri(img.img.url),
                'order': img.order,
                'created_at': img.created_at.strftime("%Y-%m-%d")
            })

        return JsonResponse({
            'code': 100,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

def get_user_mine(request):
    """获取用户的头像图片"""
    try:
        # 获取最新的 Mine 图片
        mine_image = Mine.objects.filter(
            is_delete=False
        ).order_by('-order').first()

        if not mine_image:
            return JsonResponse({
                'code': 404,
                'msg': '未找到头像图片',
                'result': None
            })

        return JsonResponse({
            'code': 100,
            'msg': 'success',
            'result': {
                'id': str(mine_image.id),
                'image_url': request.build_absolute_uri(mine_image.img.url),
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
                'code': 100,
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
            if saved_path:
                default_storage.delete(saved_path)
            return JsonResponse({
                'code': 500,
                'msg': f'上传失败: {str(e)}'
            })

    return JsonResponse({
        'code': 400,
        'msg': '无效请求或未上传图片'
    })

# app01/views.py
def get_user_mine(request):
    """获取用户的头像图片"""
    try:
        # 获取最新的 Mine 图片
        mine_image = Mine.objects.filter(
            is_delete=False
        ).order_by('-order').first()

        if not mine_image:
            return JsonResponse({
                'code': 404,
                'msg': '未找到头像图片',
                'result': None
            })

        # 构建完整的 URL
        image_url = request.build_absolute_uri(mine_image.img.url)

        return JsonResponse({
            'code': 100,
            'msg': 'success',
            'result': {
                'id': mine_image.id,  # 整数 ID
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

from django.http import HttpResponse
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
                'code': 100,
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
                'code': 100,
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