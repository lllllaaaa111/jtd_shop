from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Welcome, Banner, Article, Notice
import logging

logger = logging.getLogger(__name__)

def welcome(request):
    """获取最新的欢迎图片"""
    try:
        # 获取最新的 Welcome 图片
        welcome_image = Welcome.objects.filter(
            is_delete=False,
            is_active=True
        ).order_by('-order', '-created_at').first()

        if not welcome_image:
            logger.warning("未找到欢迎图片")
            return JsonResponse({
                'code': 404,
                'msg': '未找到欢迎图片',
                'result': None
            })

        # 构建图片 URL
        image_url = request.build_absolute_uri(welcome_image.img.url)

        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'result': {
                'id': str(welcome_image.id),
                'title': welcome_image.title,
                'image_url': image_url,
                'order': welcome_image.order,
                'created_at': welcome_image.created_at.strftime("%Y-%m-%d")
            }
        })
    except Exception as e:
        logger.exception("获取欢迎图片时发生错误")
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

def welcome_image_list(request):
    """获取欢迎图片列表"""
    try:
        # 获取所有未被删除的欢迎图片，按 order 排序
        images = Welcome.objects.filter(
            is_delete=False,
            is_active=True
        ).order_by('order', '-created_at')

        # 如果没有图片，返回默认图片
        if not images.exists():
            logger.warning("数据库中没有欢迎图片记录")
            return JsonResponse({
                'code': 200,
                'msg': 'success',
                'result': [{
                    'image_url': request.build_absolute_uri(settings.STATIC_URL + 'images/default_welcome.jpg'),
                    'title': '默认欢迎图片',
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
                'id': img.id,
                'title': img.title,
                'image_url': image_url,
                'order': img.order,
                'created_at': img.created_at.strftime("%Y-%m-%d")
            })

        return JsonResponse({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取欢迎图片列表时发生错误")
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        })

@api_view(['GET'])
def banner_list(request):
    """获取轮播图列表"""
    try:
        banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
        
        data = []
        for banner in banners:
            data.append({
                'id': banner.id,
                'title': banner.title,
                'image_url': request.build_absolute_uri(banner.image.url),
                'link_url': banner.link_url,
                'order': banner.order
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取轮播图列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def article_list(request):
    """获取文章列表"""
    try:
        articles = Article.objects.filter(is_published=True).order_by('-published_at', '-created_at')
        
        data = []
        for article in articles:
            data.append({
                'id': article.id,
                'title': article.title,
                'summary': article.summary,
                'cover_image': request.build_absolute_uri(article.cover_image.url) if article.cover_image else None,
                'author': article.author.username if article.author else '匿名',
                'published_at': article.published_at.strftime("%Y-%m-%d %H:%M:%S") if article.published_at else None
            })
        
            return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取文章列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def article_detail(request, article_id):
    """获取文章详情"""
    try:
        article = Article.objects.get(id=article_id, is_published=True)
        
        data = {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'summary': article.summary,
            'cover_image': request.build_absolute_uri(article.cover_image.url) if article.cover_image else None,
            'author': article.author.username if article.author else '匿名',
            'published_at': article.published_at.strftime("%Y-%m-%d %H:%M:%S") if article.published_at else None,
            'created_at': article.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return Response({
            'code': 200,
        'msg': 'success',
        'result': data
        })
    except Article.DoesNotExist:
        return Response({
            'code': 404,
            'msg': '文章不存在',
            'result': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("获取文章详情时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def notice_list(request):
    """获取系统公告列表"""
    try:
        notices = Notice.objects.filter(is_active=True).order_by('-is_important', '-created_at')
        
        data = []
        for notice in notices:
            data.append({
                'id': notice.id,
                'title': notice.title,
                'content': notice.content,
                'is_important': notice.is_important,
                'created_at': notice.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取系统公告列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
