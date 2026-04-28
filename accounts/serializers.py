from rest_framework import serializers
from .models import User, Employer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    role = serializers.ChoiceField(choices=['user', 'employer'], default='user')
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'name', 'bio', 'location', 'skills', 'phone',
            'linkedin', 'github', 'experience', 'education', 'avatar', 'resume'
        ]


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class EmployerPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        exclude = ['user']
