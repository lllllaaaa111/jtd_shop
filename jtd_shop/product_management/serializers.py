from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductDescription


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'parent_name', 'is_active', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'is_primary', 'order', 'created_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductDescriptionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductDescription
        fields = ['id', 'description_image', 'image_url', 'order', 'created_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.description_image and request:
            return request.build_absolute_uri(obj.description_image.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    descriptions = ProductDescriptionSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'original_price', 'stock', 'sales',
            'manufacturer', 'category', 'category_name', 'is_active', 'main_image',
            'images', 'descriptions', 'created_at', 'updated_at'
        ]
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_primary=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'original_price', 'stock', 'sales',
            'manufacturer', 'category', 'is_active'
        ]


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'original_price', 'stock', 'sales',
            'manufacturer', 'category', 'is_active'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'price': {'required': False},
            'category': {'required': False},
        }
