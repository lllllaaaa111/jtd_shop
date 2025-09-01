from rest_framework import serializers
from .models import SystemConfig, OperationLog, FileUpload, DataBackup
from user_management.models import User


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = [
            'id', 'mchid', 'serial_no', 'api_v2_key', 'api_v3_key', 'cert_file', 'key_file',
            'appid', 'app_secret', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SystemConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = [
            'mchid', 'serial_no', 'api_v2_key', 'api_v3_key', 'cert_file', 'key_file',
            'appid', 'app_secret', 'is_active'
        ]


class SystemConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = [
            'mchid', 'serial_no', 'api_v2_key', 'api_v3_key', 'cert_file', 'key_file',
            'appid', 'app_secret', 'is_active'
        ]


class OperationLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = [
            'id', 'user', 'user_name', 'action', 'resource', 'resource_id', 'description',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']


class FileUploadSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'user', 'user_name', 'file_name', 'file_path', 'file_size', 'file_size_mb',
            'file_type', 'upload_time', 'is_deleted'
        ]
        read_only_fields = ['upload_time', 'file_size_mb']


class FileUploadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['user', 'file_name', 'file_path', 'file_size', 'file_type']


class DataBackupSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DataBackup
        fields = [
            'id', 'backup_name', 'backup_type', 'file_path', 'file_size', 'description',
            'created_by', 'created_by_name', 'created_at', 'is_success'
        ]
        read_only_fields = ['created_at']


class DataBackupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBackup
        fields = ['backup_name', 'backup_type', 'file_path', 'file_size', 'description', 'created_by']
