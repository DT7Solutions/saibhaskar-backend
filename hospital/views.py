from datetime import datetime
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,generics
from django.utils.dateparse import parse_date
from django.utils.timezone import now
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
def update_appointment_status(request):
 
    new_status = "completed"
    print(new_status)
    # if not new_status:
    #     return Response({"error": "Status not provided"}, status=400)

    # try:
    #     appointment = Appointment.objects.get(pk=pk)
    #     appointment.status = new_status
    #     appointment.save()
    #     return Response({"success": True, "id": appointment.id, "status": appointment.status})
    # except Appointment.DoesNotExist:
    #     return Response({"error": "Appointment not found"}, status=404)








    


    
