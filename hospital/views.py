from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
# Create your views here.
from .serializers import UsersSerializer

# ✅ Get all users
@api_view(['GET'])
def get_users(request):
    users = Users.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Get single user by ID
@api_view(['GET'])
def get_user_detail(request, pk):
    try:
        user = Users.objects.get(pk=pk)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UsersSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)