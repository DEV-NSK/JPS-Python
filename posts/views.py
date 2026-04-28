from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from accounts.views.user_views import _save_file


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request):
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 10))
    qs = Post.objects.select_related('author').all()
    total = qs.count()
    posts = qs[(page - 1) * limit: page * limit]
    return Response({
        'posts': PostSerializer(posts, many=True, context={'request': request}).data,
        'total': total,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_post(request):
    image = ''
    if request.FILES.get('image'):
        image = _save_file(request.FILES['image'], 'posts')
    post = Post.objects.create(
        author=request.user,
        content=request.data.get('content', ''),
        image=image,
    )
    return Response(PostSerializer(post, context={'request': request}).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    if request.user.role == 'admin':
        Post.objects.filter(id=post_id).delete()
    else:
        Post.objects.filter(id=post_id, author=request.user).delete()
    Comment.objects.filter(post_id=post_id).delete()
    return Response({'message': 'Post deleted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found'}, status=404)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return Response({'likes': post.likes.count(), 'liked': liked})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    comment = Comment.objects.create(
        post_id=post_id,
        author=request.user,
        content=request.data.get('content', ''),
    )
    Post.objects.filter(id=post_id).update(comments_count=Post.objects.get(id=post_id).comments_count + 1)
    return Response(CommentSerializer(comment).data, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comments(request, post_id):
    comments = Comment.objects.filter(post_id=post_id).select_related('author')
    return Response(CommentSerializer(comments, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    if request.user.role == 'admin':
        comment = Comment.objects.filter(id=comment_id).first()
    else:
        comment = Comment.objects.filter(id=comment_id, author=request.user).first()
    if comment:
        Post.objects.filter(id=comment.post_id).update(
            comments_count=max(0, Post.objects.get(id=comment.post_id).comments_count - 1)
        )
        comment.delete()
    return Response({'message': 'Comment deleted'})
