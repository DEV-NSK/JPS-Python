from django.urls import path
from .views import get_posts, create_post, delete_post, like_post, add_comment, get_comments, delete_comment

urlpatterns = [
    path('', get_posts),
    path('create', create_post),
    path('<int:post_id>', delete_post),
    path('<int:post_id>/like', like_post),
    path('<int:post_id>/comment', add_comment),
    path('<int:post_id>/comments', get_comments),
    path('comments/<int:comment_id>', delete_comment),
]
