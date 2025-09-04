from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,generics
from .models import *
from django.contrib.auth import authenticate,get_user_model
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.



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

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful',
                'role': user.role.role_category if user.role else None, 
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
