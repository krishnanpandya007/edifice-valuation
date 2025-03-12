from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """Creates and returns a regular user with an email and password"""
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)  # Normalize the email (lowercase domain)
        user = self.model(email=email)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and returns a superuser with all permissions"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        COORDINATOR = "COORDINATOR", "Co-ordinator"
        TECHNICAL_ENGINEER = "TECHNICAL_ENGINEER", "Technical engineer"
        VALUATION_ENGINEER = "VALUATION_ENGINEER", "Valuation engineer"
        PRINCIPLE_ENGINEER = "PRINCIPLE_ENGINEER", "Principle engineer"

    role = models.CharField(
        max_length=20, choices=Roles.choices, default=Roles.TECHNICAL_ENGINEER
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)  # Make it optional
    last_name = models.CharField(max_length=30, blank=True, null=True)   # Make it optional
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional required fields

    @property
    def is_coordinator(self):
        return self.role == self.Roles.COORDINATOR

    def __str__(self):
        return self.email

class Site(models.Model):

    class NameFields(models.TextChoices):
        OWNER = "OWNER", "Owner"
        OWNERS = "OWNERS", "Owners"
        PROPOSED_OWNERS = "PROPOSED_OWNERS", "Proposed Owners"
        PROPOSED_OWNER = "PROPOSED_OWNER", "Proposed Owner"

    class ReportStatus(models.TextChoices):
        REPORT_REQUEST_SUBMITTED = "REPORT_REQUEST_SUBMITTED", "Report request submitted"
        VISIT_ASSIGNED = "VISIT_ASSIGNED", "Visit assigned"
        VISIT_COMPLETED = "VISIT_COMPLETED", "Visit completed"
        VISIT_APPROVED = "VISIT_APPROVED", "Visit approved"
        VISIT_REASSIGNED = "VISIT_REASSIGNED", "Visit reassigned"
        REPORT_GENERATED = "REPORT_GENERATED", "Report generated"
        REPORT_IN_PROGRESS = "REPORT_IN_PROGRESS", "Report in progress"
        REPORT_COMPLETED = "REPORT_COMPLETED", "Report completed"
        REPORT_SUBMITTED = "REPORT_SUBMITTED", "Report submitted"
        REPORT_APPROVED = "REPORT_APPROVED", "Report approved"
        COMPLETE = "COMPLETE", "Complete"
        REPORT_REASSIGNED = "REPORT_REASSIGNED", "Report reassigned"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Payment pending"
        DELAYED = "DELAYED", "Payment delayed"
        CANCELLED = "CANCELLED", "Payment cancelled"
        RECEIVED = "RECEIVED", "Payment received" 
    
    name = models.CharField(max_length=70, default='Unknown site')
    
    report_status = models.CharField(max_length=25, choices=ReportStatus.choices, default=ReportStatus.REPORT_REQUEST_SUBMITTED)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    bank_contact_person_name = models.CharField(max_length=70)
    bank_contact_person_number = models.CharField(max_length=16)
    property_contact_person_name = models.CharField(max_length=70)
    property_contact_person_number = models.CharField(max_length=16)
    visit_due_date = models.DateField(blank=True, null=True, default=timezone.now)
    name_field_title = models.CharField(max_length=20, choices=NameFields.choices, default=NameFields.OWNER)
    name_field_value = models.CharField(max_length=70)
    intended_purchaser_name = models.CharField(max_length=70)
    property_location = models.TextField(max_length=300)
    branch_name_address = models.TextField(max_length=350)
    borrowal_unit = models.TextField(max_length=350)
    customer_details_name = models.CharField(max_length=70)
    customer_details_application_number = models.CharField(max_length=20)
    property_details_address = models.TextField(max_length=300)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def get_report_status_color(self):
        report_status_colors = {
            "REPORT_REQUEST_SUBMITTED": "blue",
            "VISIT_ASSIGNED": "yellow",
            "VISIT_COMPLETED": "green",
            "VISIT_APPROVED": "green",
            "VISIT_REASSIGNED": "lime",
            "REPORT_GENERATED": "purple",
            "REPORT_IN_PROGRESS": "blue",
            "REPORT_COMPLETED": "green",
            "REPORT_SUBMITTED": "cyan",
            "REPORT_APPROVED": "green",
            "COMPLETE": "indigo",
            "REPORT_REASSIGNED": "lime"
        }
        return report_status_colors[self.report_status]
    
    @property
    def get_payment_status_color(self):
        payment_status_colors = {
            "PENDING": "yellow",
            "DELAYED": "orange",
            "CANCELLED": "red",
            "RECEIVED": "green"
        }
        return payment_status_colors[self.payment_status]

class Document(models.Model):

    site = models.ForeignKey(Site, on_delete=models.CASCADE ,related_name='documents')
    attachment = models.FileField(upload_to='uploads/')


class Comment(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE ,related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='comments')
    comment = models.TextField(max_length=350)
    posted_on = models.DateTimeField(auto_now_add=True) 


    
