from rest_framework import serializers
from .models import *

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class DoctorUnavailableDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorUnavailableDate
        fields = '__all__'
    