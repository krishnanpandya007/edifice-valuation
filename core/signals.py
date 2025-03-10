from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import CustomUser
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
            print("HI")

            password_reset_link = signer.sign_object({"user_id": instance.pk}) 
            print("HI")

            if settings.DEBUG:
                base_url = "http://localhost:8000"
            else:
                base_url = f"https://{settings.ALLOWED_HOSTS[-1]}"
            print("HI")
            
            send_mail("Edifice website account access","password reset", settings.EMAIL_HOST_USER, [instance.email], html_message=message.format(instance.email, f"{base_url}/password-reset/{password_reset_link}") )
            print("HI")
        
        except Exception as e:

            print("[ERR]: ", e)

