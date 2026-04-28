from rest_framework import serializers
from .models import Application
from accounts.serializers import UserSerializer
from jobs.serializers import JobSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_detail = UserSerializer(source='applicant', read_only=True)
    job_detail = JobSerializer(source='job', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['id', 'applicant', 'created_at', 'updated_at']
