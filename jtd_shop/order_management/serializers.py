from rest_framework import serializers
from .models import Order, OrderItem, Cart, OrderStatusLog
from user_management.models import User
from product_management.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price', 'total_price']
        read_only_fields = ['total_price']
    
    def get_product_image(self, obj):
        main_image = obj.product.images.filter(is_primary=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'total_amount', 'status', 'status_display',
            'payment_method', 'payment_method_display', 'shipping_address', 'delivery_address',
            'recipient_name', 'recipient_phone', 'notes', 'items', 'created_at', 'updated_at',
            'paid_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'user', 'total_amount', 'payment_method', 'shipping_address', 'delivery_address',
            'recipient_name', 'recipient_phone', 'notes'
        ]


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'status', 'payment_method', 'shipping_address', 'delivery_address',
            'recipient_name', 'recipient_phone', 'notes', 'paid_at', 'shipped_at', 'delivered_at'
        ]
        extra_kwargs = {
            'status': {'required': False},
        }


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'product', 'product_name', 'product_price', 'product_image',
            'quantity', 'price', 'total_price', 'added_at', 'updated_at'
        ]
        read_only_fields = ['total_price', 'added_at', 'updated_at']
    
    def get_product_image(self, obj):
        main_image = obj.product.images.filter(is_primary=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None


class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'product', 'quantity', 'price']


class CartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['quantity', 'price']


class OrderStatusLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = OrderStatusLog
        fields = [
            'id', 'order', 'from_status', 'to_status', 'operator', 'operator_name',
            'notes', 'created_at'
        ]
        read_only_fields = ['created_at']
