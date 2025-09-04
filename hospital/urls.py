from django.urls import path
from .views import get_users, get_user_detail

urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/<int:pk>/', get_user_detail, name='get_user_detail'),
]