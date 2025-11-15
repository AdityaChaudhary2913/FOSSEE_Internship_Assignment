"""
Serializers for the Equipment application.
Handles data validation and transformation for API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, EquipmentData


class EquipmentDataSerializer(serializers.ModelSerializer):
    """Serializer for individual equipment data."""
    
    class Meta:
        model = EquipmentData
        fields = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']
        
    def validate_flowrate(self, value):
        """Ensure flowrate is positive."""
        if value < 0:
            raise serializers.ValidationError("Flowrate must be a positive number.")
        return value
    
    def validate_pressure(self, value):
        """Ensure pressure is positive."""
        if value < 0:
            raise serializers.ValidationError("Pressure must be a positive number.")
        return value


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for dataset with summary statistics."""
    equipment_items = EquipmentDataSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'user_username', 'uploaded_at',
            'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'equipment_type_distribution', 'equipment_items'
        ]
        read_only_fields = [
            'id', 'uploaded_at', 'total_count', 'avg_flowrate',
            'avg_pressure', 'avg_temperature', 'equipment_type_distribution'
        ]


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset summaries (without detailed equipment items)."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'user_username', 'uploaded_at',
            'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'equipment_type_distribution'
        ]


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file upload."""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate that the uploaded file is a CSV."""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must not exceed 5MB.")
        
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        """Create a new user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
