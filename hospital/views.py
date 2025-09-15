from datetime import datetime
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,generics
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password,make_password
from .emails import send_appointment_email 
from .models import *
from django.contrib.auth import authenticate,get_user_model
from django.http import JsonResponse
from .serializers import *

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

# login 
@api_view(['POST'])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)

        if user:
            return Response({
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "fname": user.first_name,
                    "lname": user.last_name,
                    "username":user.username,
                    "phonenumber":user.phone,
                    "role": user.role.role_category if hasattr(user, 'role') and user.role else None,
                },
                "message": "Login successful",
                "status_code": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response({
            "data": None,
            "message": "Invalid Credentials please check and try Agian",
            "status_code": status.HTTP_401_UNAUTHORIZED
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "data": serializer.errors,
        "message": "Invalid data format",
        "status_code": status.HTTP_400_BAD_REQUEST
    }, status=status.HTTP_400_BAD_REQUEST)
    
# logout 
@api_view(['POST'])
def logout_view(request):
    request.session.flush() 
    return Response({
        "message": "Logout successful",
        "status_code": status.HTTP_200_OK
    }, status=status.HTTP_200_OK)

#  Get all blocked dates for a doctor
@api_view(['GET'])
def get_blocked_dates(request, doctor_id):
    today = datetime.now().date()  

    blocked_dates = DoctorUnavailableDate.objects.filter(
        doctor_id=doctor_id,
        date__gte=today
    ).order_by('date')
    serializer = DoctorUnavailableDateSerializer(blocked_dates, many=True)
    return Response(serializer.data)

#  Block a date
@api_view(['POST'])
def block_date(request):
    doctor_id = request.data.get('doctor')
    date = request.data.get('date')

    if not doctor_id or not date:
        return Response({"error": "doctor_id and date are required"}, status=status.HTTP_400_BAD_REQUEST)

    exists = DoctorUnavailableDate.objects.filter(doctor_id=doctor_id, date=date).exists()
    if exists:
        return Response({"error": "Date already blocked"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = DoctorUnavailableDateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Unblock a date
@api_view(['DELETE'])
def unblock_date(request, doctor_id, date):
    try:
        blocked_date = DoctorUnavailableDate.objects.get(doctor_id=doctor_id, date=date)
        blocked_date.delete()
        return Response({"message": "Date unblocked"}, status=status.HTTP_200_OK)
    except DoctorUnavailableDate.DoesNotExist:
        return Response({"error": "Date not found"}, status=status.HTTP_404_NOT_FOUND)

# book appointment    
@api_view(['POST'])
def book_appointment(request):
    try:
        data = request.data

        # Create or get patient
        patient, _ = Patient.objects.get_or_create(
            name=data.get("name"),
            phone=data.get("phone"),
            defaults={"email": data.get("email")}
        )

        # Find doctor
        try:
            doctor = Users.objects.get(id=data.get("doctor"))
        except Users.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create appointment
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            service=data.get("service"),
            appointment_date=parse_date(data.get("appointment_date")),
            status="pending"
        )

        return Response({"message": "Appointment booked successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Today and Upcoming appointments 
@api_view(['GET'])
def get_appointments(request, doctor_id):  # doctor_id now comes from URL
    today = now().date()

    appointments = Appointment.objects.filter(doctor_id=doctor_id)

    today_appointments = appointments.filter(appointment_date=today).select_related("patient")
    upcoming_appointments = appointments.filter(appointment_date__gt=today).select_related("patient")

    return JsonResponse({
        "today": [
            {
                "id": appt.id, 
                "user_name": appt.patient.name,
                "user_email": appt.patient.email,
                "user_phone": appt.patient.phone,
                "appointment_date": appt.appointment_date.strftime("%Y-%m-%d"),
                "status": appt.status
            }
            for appt in today_appointments
        ],
        "upcoming": [
            {
                "id": appt.id, 
                "user_name": appt.patient.name,
                "user_email": appt.patient.email,
                "user_phone": appt.patient.phone,
                "appointment_date": appt.appointment_date.strftime("%Y-%m-%d"),
                "status": appt.status
            }
            for appt in upcoming_appointments
        ]
    })

# update appointment status 
@api_view(['POST'])
def update_appointment_status(request, id, status):
    if not status:
        return Response({"error": "Status not provided"}, status=400)
   
    try:
        appointment = Appointment.objects.get(pk=id)
        appointment.status = status
        appointment.save()
        # Send email to patient
        if appointment.patient.email:
            send_appointment_email(
                user_email=appointment.patient.email,
                patient_name=appointment.patient.name,
                appointment=appointment,
                status=status
            )
        return Response({"success": True, "id": appointment.id, "status": appointment.status})
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=404)
    
# profile save and update 
@api_view(['GET', 'PUT'])
def user_profile(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            "id": user.id,
            "email": user.email,
            "fname": user.first_name,
            "lname": user.last_name,
            "username": user.username,
            "phonenumber": user.phone,
            "date_of_birth": user.date_of_birth,
            "pincode": user.pincode,
            "address": user.address,
        })

    elif request.method == 'PUT':
        # Handle the field name mapping for updates
        data = request.data
        
        # Map frontend field names to model field names and update
        if 'fname' in data:
            user.first_name = data['fname']
        if 'lname' in data:
            user.last_name = data['lname']
        if 'phonenumber' in data:
            user.phone = data['phonenumber']
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'date_of_birth' in data:
            user.date_of_birth = data['date_of_birth']
        if 'pincode' in data:
            user.pincode = data['pincode']
        if 'address' in data:
            user.address = data['address']
            
        user.save()
        
        return Response({
            "id": user.id,
            "email": user.email,
            "fname": user.first_name,
            "lname": user.last_name,
            "username": user.username,
            "phonenumber": user.phone,
            "date_of_birth": user.date_of_birth,
            "pincode": user.pincode,
            "address": user.address,
        })

# change password 
@api_view(['PUT'])
def change_password(request, user_id):
    x = user_id
    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return Response({"message": "User not found"}, status=404)

    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"message": list(serializer.errors.values())[0][0]}, status=400)

    current_password = serializer.validated_data['current_password']
    new_password = serializer.validated_data['new_password']

    # Use model method check_password
    if not user.check_password(current_password):
        return Response({"message": "Current password is incorrect"}, status=400)

    if user.check_password(new_password):
        return Response({"message": "New password must be different"}, status=400)

    # Set new password and save
    user.password = make_password(new_password)
    user.save()

    return Response({"message": "Password updated successfully"}, status=200)











    


    
