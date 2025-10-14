from django.core.mail import send_mail
from django.conf import settings

def send_appointment_email(user_email, patient_name, appointment, status):
    """
    Sends appointment confirmation/cancellation email to the patient.
    """
    subject = f"Your Appointment is {status.capitalize()} - BMR-Saibhaskar Hospitals"

    # Get doctor name safely
    if hasattr(appointment.doctor, 'first_name') and appointment.doctor.first_name:
        doctor_name = f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}".strip()
    else:
        doctor_name = f"Dr. {appointment.doctor.username}"

    if status.lower() == "confirmed":
        message = f"""
Dear {patient_name},

Your appointment has been CONFIRMED.

Appointment Details:
- Doctor: {doctor_name}
- Date: {appointment.appointment_date}
- Service: {appointment.service}

Please show this email when you arrive.

Best regards,  
BMR-Saibhaskar Hospitals

Contact: bmrsaibhaskarhospitals@gmail.com
        """
    elif status.lower() == "cancelled":
        message = f"""
Dear {patient_name},

Unfortunately, your appointment has been CANCELLED.

Appointment Details:
- Doctor: {doctor_name}
- Date: {appointment.appointment_date}
- Service: {appointment.service}

Please contact us to reschedule.

Best regards,  
BMR-Saibhaskar Hospitals

Contact: bmrsaibhaskarhospitals@gmail.com
        """
    else:
        message = f"""
Dear {patient_name},

Your appointment status has been updated to: {status.upper()}

Appointment Details:
- Doctor: {doctor_name}
- Date: {appointment.appointment_date}
- Service: {appointment.service}

Best regards,  
BMR-Saibhaskar Hospitals

Contact: bmrsaibhaskarhospitals@gmail.com
        """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )