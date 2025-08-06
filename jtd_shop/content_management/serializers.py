from rest_framework import serializers
from .models import Welcome, Banner, Article, Notice
from user_management.models import User


class WelcomeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Welcome
        fields = ['id', 'title', 'img', 'image_url', 'order', 'is_active', 'is_delete', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.img and request:
            return request.build_absolute_uri(obj.img.url)
        return None


class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'image_url', 'link_url', 'order', 'is_active', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['created_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'summary', 'author', 'author_name', 'cover_image', 'cover_image_url',
            'is_published', 'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'content', 'summary', 'author', 'cover_image', 'is_published', 'published_at']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'content', 'summary', 'cover_image', 'is_published', 'published_at']
        extra_kwargs = {
            'title': {'required': False},
            'content': {'required': False},
        }


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'is_important', 'is_active', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['created_at']


class NoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_important', 'is_active', 'start_time', 'end_time']


class NoticeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_important', 'is_active', 'start_time', 'end_time']
        extra_kwargs = {
            'title': {'required': False},
            'content': {'required': False},
        }
