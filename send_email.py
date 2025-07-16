from django.core.mail import send_mail

send_mail(
    subject='SMTP Test',
    message='SMTP connection and email test successful.',
    from_email='ummemuna14@gmail.com',         
    recipient_list=['ummemuna14@gmail.com'],  
    fail_silently=False,
)
