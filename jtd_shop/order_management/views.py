from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Cart, OrderStatusLog
from user_management.models import User
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    """获取用户订单列表"""
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'order_number': order.order_number,
                'total_amount': str(order.total_amount),
                'status': order.status,
                'status_display': order.get_status_display(),
                'payment_method': order.payment_method,
                'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'paid_at': order.paid_at.strftime("%Y-%m-%d %H:%M:%S") if order.paid_at else None,
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取订单列表时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """获取订单详情"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # 获取订单商品
        items = order.items.all()
        item_list = []
        for item in items:
            item_list.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.price),
                'total_price': str(item.total_price)
            })
        
        data = {
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': str(order.total_amount),
            'status': order.status,
            'status_display': order.get_status_display(),
            'payment_method': order.payment_method,
            'shipping_address': order.shipping_address,
            'delivery_address': order.delivery_address,
            'recipient_name': order.recipient_name,
            'recipient_phone': order.recipient_phone,
            'notes': order.notes,
            'items': item_list,
            'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'paid_at': order.paid_at.strftime("%Y-%m-%d %H:%M:%S") if order.paid_at else None,
            'shipped_at': order.shipped_at.strftime("%Y-%m-%d %H:%M:%S") if order.shipped_at else None,
            'delivered_at': order.delivered_at.strftime("%Y-%m-%d %H:%M:%S") if order.delivered_at else None,
        }
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Order.DoesNotExist:
        return Response({
            'code': 404,
            'msg': '订单不存在',
            'result': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("获取订单详情时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_list(request):
    """获取用户购物车"""
    try:
        cart_items = Cart.objects.filter(user=request.user).order_by('-added_at')
        data = []
        for item in cart_items:
            data.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.price),
                'total_price': str(item.total_price),
                'added_at': item.added_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': data
        })
    except Exception as e:
        logger.exception("获取购物车时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
