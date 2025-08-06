from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category, Product, ProductImage, ProductDescription
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def category_list(request):
    """获取商品分类列表"""
    try:
        categories = Category.objects.filter(is_active=True)
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'parent_id': category.parent.id if category.parent else None,
                'parent_name': category.parent.name if category.parent else None,
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取商品分类列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def product_list(request):
    """获取商品列表"""
    try:
        products = Product.objects.filter(is_active=True).order_by('-created_at')
        data = []
        for product in products:
            # 获取主图
            main_image = product.images.filter(is_primary=True).first()
            main_image_url = request.build_absolute_uri(main_image.image.url) if main_image else None
            
            data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'original_price': str(product.original_price) if product.original_price else None,
                'stock': product.stock,
                'sales': product.sales,
                'manufacturer': product.manufacturer,
                'category_id': product.category.id,
                'category_name': product.category.name,
                'main_image': main_image_url,
                'created_at': product.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取商品列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def product_detail(request, product_id):
    """获取商品详情"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # 获取所有图片
        images = product.images.order_by('order', '-created_at')
        image_list = []
        for img in images:
            image_list.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.image.url),
                'is_primary': img.is_primary,
                'order': img.order
            })
        
        # 获取描述图片
        descriptions = product.descriptions.order_by('order', '-created_at')
        description_list = []
        for desc in descriptions:
            if desc.description_image:
                description_list.append({
                    'id': desc.id,
                    'image_url': request.build_absolute_uri(desc.description_image.url),
                    'order': desc.order
                })
        
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'original_price': str(product.original_price) if product.original_price else None,
            'stock': product.stock,
            'sales': product.sales,
            'manufacturer': product.manufacturer,
            'category_id': product.category.id,
            'category_name': product.category.name,
            'images': image_list,
            'description_images': description_list,
            'created_at': product.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': product.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Product.DoesNotExist:
        return Response({
            'code': 404,
            'msg': '商品不存在',
            'result': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("获取商品详情时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
