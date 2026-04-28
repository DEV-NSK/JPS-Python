from django.urls import path
from accounts.views.admin_views import (
    get_stats, get_all_users, delete_user,
    get_all_jobs, get_all_posts, delete_post
)

urlpatterns = [
    path('stats', get_stats),
    path('users', get_all_users),
    path('users/<int:user_id>', delete_user),
    path('jobs', get_all_jobs),
    path('posts', get_all_posts),
    path('post/<int:post_id>', delete_post),
]
