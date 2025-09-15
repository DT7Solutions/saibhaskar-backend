from django.urls import path
from .views import *

urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/<int:pk>/', get_user_detail, name='get_user_detail'),
    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    path('blocked-dates/<int:doctor_id>/', get_blocked_dates, name='get_blocked_dates'),
    path('block-date/', block_date, name='block_date'),
    path('unblock-date/<int:doctor_id>/<str:date>/', unblock_date, name='unblock_date'),
    path("book-appointment/", book_appointment, name="book_appointment"),
    path("appointments/<int:doctor_id>/", get_appointments, name="get_appointments"),
    path('update-appointment-status/<int:id>/<str:status>/', update_appointment_status, name='update_appointment_status'),
    path('user-profile/<int:user_id>/', user_profile, name='user_profile'),
    path('change-password/<int:user_id>/', change_password, name='change_password'),

]