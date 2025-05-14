from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import CustomUser, Site
from django.core.mail import send_mail
from django.core.signing import Signer
from django.conf import settings

@receiver(post_save, sender=CustomUser) 
def create_profile(sender, instance, created, **kwargs):

    if created:
        print("HI")
        try:

            # send mail for password reset 
            message = '''

            Hello,
            <br/>
            Your account on edifice has been registered, to gain access of it kindly note your email/username and reset password by clicking on provided link.
            <br/>
            <b>Username</b>: {}
            <b>Password update link</b>: <a href="{}">Click here</a>

            '''
            
            signer = Signer()

            password_reset_link = signer.sign_object({"user_id": instance.pk}) 

            if settings.DEBUG:
                base_url = "https://20b0-2409-40c1-3002-3772-287f-3bd6-8ce2-d8bb.ngrok-free.app"
            else:
                base_url = f"https://{settings.ALLOWED_HOSTS[-1]}"
            
            send_mail("Edifice website account access","password reset", settings.EMAIL_HOST_USER, [instance.email], html_message=message.format(instance.email, f"{base_url}/password-reset/{password_reset_link}") )
        
        except Exception as e:

            print("[ERR]: ", e)


@receiver(post_save, sender=Site) 
def notify_assignment(sender, instance, created, **kwargs):

    if hasattr(instance, "_notify") and hasattr(instance, "_assignee_email"):
        send_mail("New site assigned", "", settings.EMAIL_HOST_USER, [instance._assignee_email], html_message=f'''You are assigned to,<br/> Site: <b>{instance.application_details.branch_name}</b><br/>Visit due date: <b>{instance.application_details.due_date_for_visit}</b><br/><br/><a href="{"http" if settings.DEBUG else "https"}://{settings.ALLOWED_HOSTS[-1]}/">Click here</a> to know more.''')

