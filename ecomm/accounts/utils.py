from django.conf import settings
from twilio.rest import Client
from django.core.mail import send_mail

# Initialize Twilio client with settings
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Function to send OTP SMS
def send_otp_sms(phone_number, otp):
    try:
        message = client.messages.create(
            body=f'Your OTP for login is: {otp}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"OTP SMS sent to {phone_number} with message SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send OTP SMS to {phone_number}: {e}")


def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP for login is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)