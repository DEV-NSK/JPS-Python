from django.urls import path
from accounts.views.auth_views import register, login, get_me

urlpatterns = [
    path('register', register),
    path('login', login),
    path('me', get_me),
]
