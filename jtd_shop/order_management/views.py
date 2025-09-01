from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Cart, OrderStatusLog
from user_management.models import User
import logging
from django.utils import timezone

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

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """从购物车创建订单"""
    try:
        # 获取用户购物车中的商品
        cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response({
                'code': 400,
                'msg': '购物车为空，无法创建订单',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证请求数据
        required_fields = ['delivery_address', 'recipient_name', 'recipient_phone']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'code': 400,
                    'msg': f'缺少必填字段: {field}',
                    'result': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 计算总金额
        total_amount = sum(item.total_price for item in cart_items)
        
        # 创建订单
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            delivery_address=request.data.get('delivery_address'),
            recipient_name=request.data.get('recipient_name'),
            recipient_phone=request.data.get('recipient_phone'),
            shipping_address=request.data.get('shipping_address', ''),
            notes=request.data.get('notes', ''),
            payment_method=request.data.get('payment_method', '')
        )
        
        # 创建订单商品项
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                total_price=cart_item.total_price
            )
            order_items.append(order_item)
        
        # 清空购物车
        cart_items.delete()
        
        # 记录订单状态日志
        OrderStatusLog.objects.create(
            order=order,
            from_status='',
            to_status='pending',
            operator=request.user,
            notes='订单创建'
        )
        
        # 返回订单信息
        data = {
            'id': order.id,
            'order_number': order.order_number,
            'internal_order_number': getattr(order, 'internal_order_number', None),
            'total_amount': str(order.total_amount),
            'status': order.status,
            'status_display': order.get_status_display(),
            'delivery_address': order.delivery_address,
            'recipient_name': order.recipient_name,
            'recipient_phone': order.recipient_phone,
            'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'items_count': len(order_items)
        }
        
        return Response({
            'code': 200,
            'msg': '订单创建成功',
            'result': data
        })
        
    except Exception as e:
        logger.exception("创建订单时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_direct(request):
    """直接创建订单（不依赖购物车）
    请求体:
    {
      "items": [{"product_id": 1, "quantity": 2}, ...],  // 至少一项
      "delivery_address": "收货地址",
      "recipient_name": "收件人",
      "recipient_phone": "手机号",
      "shipping_address": "发货地址(可选)",
      "notes": "备注(可选)",
      "payment_method": "wechat|alipay|bank(可选)"
    }
    """
    try:
        data = request.data if isinstance(request.data, dict) else {}
        items = data.get('items') or []
        if not isinstance(items, list) or not items:
            return Response({
                'code': 400,
                'msg': 'items 不能为空且必须为数组',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        # 基本字段校验
        for f in ['delivery_address', 'recipient_name', 'recipient_phone']:
            if not data.get(f):
                return Response({
                    'code': 400,
                    'msg': f'缺少必填字段: {f}',
                    'result': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 汇总价格并校验商品
        from product_management.models import Product
        total_amount = 0
        normalized = []
        for it in items:
            try:
                pid = int(it.get('product_id'))
                qty = int(it.get('quantity'))
                if qty <= 0:
                    return Response({'code':400,'msg':'quantity 必须大于0','result':None}, status=400)
            except Exception:
                return Response({'code':400,'msg':'product_id/quantity 非法','result':None}, status=400)
            product = get_object_or_404(Product, id=pid)
            line_total = product.price * qty
            total_amount += line_total
            normalized.append((product, qty, product.price, line_total))
        
        # 创建订单
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            delivery_address=data.get('delivery_address'),
            recipient_name=data.get('recipient_name'),
            recipient_phone=data.get('recipient_phone'),
            shipping_address=data.get('shipping_address') or '',
            notes=data.get('notes') or '',
            payment_method=data.get('payment_method') or ''
        )
        
        # 创建订单项
        for product, qty, unit_price, line_total in normalized:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=unit_price,
                total_price=line_total
            )
        
        OrderStatusLog.objects.create(
            order=order,
            from_status='',
            to_status='pending',
            operator=request.user,
            notes='直接新建订单'
        )
        
        return Response({
            'code': 200,
            'msg': '订单创建成功',
            'result': {
                'id': order.id,
                'order_number': order.order_number,
                'internal_order_number': getattr(order, 'internal_order_number', None),
                'total_amount': str(order.total_amount),
                'status': order.status,
                'status_display': order.get_status_display(),
                'delivery_address': order.delivery_address,
                'recipient_name': order.recipient_name,
                'recipient_phone': order.recipient_phone,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        logger.exception("直接创建订单时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request):
    """根据内部订单号更新订单支付状态
    请求体示例:
    {"internal_order_number": "000000000123", "status": "paid", "payment_method": "wechat"}
    支持的状态见 Order.STATUS_CHOICES
    若状态为 paid，将自动写入 paid_at 时间戳
    """
    try:
        internal_no = request.data.get('internal_order_number')
        new_status = request.data.get('status')
        payment_method = request.data.get('payment_method')
        if not internal_no or not new_status:
            return Response({
                'code': 400,
                'msg': '缺少必填字段: internal_order_number 或 status',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        allowed_status = [c[0] for c in Order.STATUS_CHOICES]
        if new_status not in allowed_status:
            return Response({
                'code': 400,
                'msg': f'非法状态: {new_status}',
                'result': {
                    'allowed': allowed_status
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order = get_object_or_404(Order, internal_order_number=internal_no, user=request.user)
        old_status = order.status
        
        order.status = new_status
        if payment_method:
            order.payment_method = payment_method
        if new_status == 'paid' and not order.paid_at:
            order.paid_at = timezone.now()
        order.save()
        
        OrderStatusLog.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            operator=request.user,
            notes='状态更新接口'
        )
        
        return Response({
            'code': 200,
            'msg': '订单状态更新成功',
            'result': {
                'internal_order_number': order.internal_order_number,
                'order_number': order.order_number,
                'status': order.status,
                'payment_method': order.payment_method,
                'paid_at': order.paid_at.strftime('%Y-%m-%d %H:%M:%S') if order.paid_at else None
            }
        })
    except Order.DoesNotExist:
        return Response({
            'code': 404,
            'msg': '订单不存在',
            'result': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("更新订单状态时发生错误")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
