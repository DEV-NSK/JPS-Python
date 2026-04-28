from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsAdmin
from accounts.serializers import UserSerializer
from jobs.models import Job
from jobs.serializers import JobSerializer
from applications.models import Application
from posts.models import Post, Comment
from posts.serializers import PostSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_stats(request):
    return Response({
        'users': User.objects.filter(role='user').count(),
        'employers': User.objects.filter(role='employer').count(),
        'jobs': Job.objects.count(),
        'applications': Application.objects.count(),
        'posts': Post.objects.count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_all_users(request):
    users = User.objects.exclude(role='admin').order_by('-created_at')
    return Response(UserSerializer(users, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_user(request, user_id):
    User.objects.filter(id=user_id).delete()
    return Response({'message': 'User deleted'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_all_jobs(request):
    jobs = Job.objects.select_related('employer').order_by('-created_at')
    return Response(JobSerializer(jobs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_all_posts(request):
    posts = Post.objects.select_related('author').order_by('-created_at')
    return Response(PostSerializer(posts, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_post(request, post_id):
    Post.objects.filter(id=post_id).delete()
    Comment.objects.filter(post_id=post_id).delete()
    return Response({'message': 'Post deleted'})
