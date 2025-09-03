from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords


# -------------------------------
# User Manager
# -------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone=phone
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password=None):
        user = self.create_user(email, username, phone, password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# -------------------------------
# Role Model
# -------------------------------
class Role(models.Model):
    ROLE_CATEGORIES = [
        ("admin", "Admin"),
        ("doctor", "Doctor"),
    ]
    
    role_name = models.CharField(max_length=100, unique=True)
    role_category = models.CharField(max_length=100, choices=ROLE_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.role_name

    class Meta:
        db_table = 'role'


# -------------------------------
# Users (Doctor / Admin)
# -------------------------------
class Users(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)

    profile_image = models.TextField(blank=True, null=True)
    firebase_id = models.TextField(blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    pincode = models.IntegerField(blank=True, null=True, default=None)
    address = models.TextField(blank=True, null=True, default=None)
    otp = models.IntegerField(blank=True, null=True, default=None)

    # Link role (Admin or Doctor)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone"]

    objects = UserManager()
    history = HistoricalRecords()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"

class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Users, on_delete=models.CASCADE, limit_choices_to={'role__role_category': 'doctor'})
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "appointment_date", "appointment_time")

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.username} ({self.appointment_date})"

class DoctorUnavailableDate(models.Model):
    doctor = models.ForeignKey(Users, on_delete=models.CASCADE, limit_choices_to={'role__role_category': 'doctor'})
    date = models.DateField()

    class Meta:
        unique_together = ("doctor", "date")

    def __str__(self):
        return f"{self.doctor.username} unavailable on {self.date}"
