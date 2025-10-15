from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

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

    # Prepare common HTML structure
    logo_url = "https://saibhaskarhospital.com/assets/img/saibhaskar-logo.png"

    if status.lower() == "confirmed":
        status_message = "Your appointment has been <strong style='color:green;'>CONFIRMED</strong>."
    elif status.lower() == "cancelled":
        status_message = "Unfortunately, your appointment has been <strong style='color:red;'>CANCELLED</strong>."
    else:
        status_message = f"Your appointment status has been updated to: <strong>{status.upper()}</strong>."

    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color:#f9f9f9; padding:20px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto; background:white; border:1px solid #ddd; border-radius:8px;">
        <tr>
          <td align="center" style="padding:13px;">
            <img src="{logo_url}" alt="Sai Bhaskar Hospitals" width="150" style="display:block; margin:auto;">
          </td>
        </tr>
        <tr>
          <td style="padding:13px; font-size:15px; color:#333;">
            <p>Dear {patient_name},</p>
            <p>{status_message}</p>

            <table cellpadding="6" cellspacing="0" width="100%" style="border:1px solid #ccc; border-collapse:collapse; margin-top:10px;">
              <tr>
                <td style="border:1px solid #ccc; font-weight:bold;">Doctor</td>
                <td style="border:1px solid #ccc;">{doctor_name}</td>
              </tr>
              <tr>
                <td style="border:1px solid #ccc; font-weight:bold;">Date</td>
                <td style="border:1px solid #ccc;">{appointment.appointment_date}</td>
              </tr>
              <tr>
                <td style="border:1px solid #ccc; font-weight:bold;">Service</td>
                <td style="border:1px solid #ccc;">{appointment.service}</td>
              </tr>
              <tr>
                <td style="border:1px solid #ccc; font-weight:bold;">Branch</td>
                <td style="border:1px solid #ccc;">{appointment.branch}</td>
              </tr>
            </table>

            <p style="margin-top:20px;">Best regards,<br>
            <strong>BMR-Saibhaskar Hospitals</strong></p>

            <p style="font-size:13px; color:#777;">Contact: <a href="mailto:bmrsaibhaskarhospitals@gmail.com">bmrsaibhaskarhospitals@gmail.com</a></p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    # Plain text version (fallback)
    plain_message = f"""
Dear {patient_name},

{status_message.replace('<strong>', '').replace('</strong>', '')}

Appointment Details:
- Doctor: {doctor_name}
- Date: {appointment.appointment_date}
- Service: {appointment.service}

Best regards,
BMR-Saibhaskar Hospitals
Contact: bmrsaibhaskarhospitals@gmail.com
    """

    # Use EmailMultiAlternatives to send HTML and text
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
