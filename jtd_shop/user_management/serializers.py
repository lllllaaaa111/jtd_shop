from rest_framework import serializers
from .models import User, UserProfile, Address, Mine


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'nickname', 'bio', 'birth_date', 'gender']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 'avatar',
            'role', 'is_active', 'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone', 'avatar',
            'role', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密码和确认密码不匹配")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone', 'avatar', 'role'
        ]
        extra_kwargs = {
            'email': {'required': False},
        }


class AddressSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'user_name', 'recipient', 'address', 'contact', 'is_default'
        ]


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['user', 'recipient', 'address', 'contact', 'is_default']


class AddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['recipient', 'address', 'contact', 'is_default']
        extra_kwargs = {
            'recipient': {'required': False},
            'address': {'required': False},
            'contact': {'required': False},
        }


class MineSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Mine
        fields = [
            'id', 'name', 'img', 'image_url', 'order', 'user', 'user_name',
            'file_size', 'created_at', 'updated_at', 'is_delete'
        ]
        read_only_fields = ['created_at', 'updated_at', 'file_size']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.img and request:
            return request.build_absolute_uri(obj.img.url)
        return None
    
    def get_file_size(self, obj):
        return obj.file_size


class MineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mine
        fields = ['name', 'img', 'order', 'user']


class MineUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mine
        fields = ['name', 'img', 'order', 'is_delete']
        extra_kwargs = {
            'name': {'required': False},
            'img': {'required': False},
        }
