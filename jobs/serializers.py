from rest_framework import serializers
from .models import Job, Bookmark


class JobSerializer(serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()
    employer_name = serializers.CharField(source='employer.name', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['id', 'employer', 'applicants_count', 'created_at', 'updated_at']

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, job=obj).exists()
        return False


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        exclude = ['employer', 'applicants_count', 'created_at', 'updated_at']


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'
