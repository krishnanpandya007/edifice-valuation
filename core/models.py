from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from num2words import num2words

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
    
    
    report_status = models.CharField(max_length=25, choices=ReportStatus.choices, default=ReportStatus.REPORT_REQUEST_SUBMITTED)
    
    creator = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='created_sites', null=True, blank=True)

    # valuation_report_pdf = models.FileField(upload_to='uploads/valuation_reports/pdf/', null=True)
    # valuation_report_docx = models.FileField(upload_to='uploads/valuation_reports/docx/', null=True)

    assignees = models.ManyToManyField(CustomUser, related_name='assigned_sites')
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
    

class Document(models.Model):

    site = models.ForeignKey(Site, on_delete=models.CASCADE ,related_name='attachments')
    name = models.CharField(max_length=70, null=True, blank=True)
    attachment = models.FileField(upload_to='uploads/')

class ImageAttachment(models.Model):
    name = models.CharField(max_length=70, null=True, blank=True)
    attachment = models.FileField(upload_to='uploads/images/')


class Comment(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE ,related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='comments')
    comment = models.TextField(max_length=350)
    posted_on = models.DateTimeField(auto_now_add=True) 

# class Site(models.Model):

#     '''
#     @on_create => create 9 section/instances and attach them with Site model with related_name
#     '''

class FieldManager(models.Model):

    field_name = models.CharField(max_length=70, unique=True)
    section_name = models.CharField(max_length=70, default='application_details')
    display_name = models.CharField(max_length=100)
    field_type = models.CharField(
        max_length=40, 
        choices=[
            ('auto-calculate', 'Auto calculate'),
            ('textbox-percentage', 'textbox-percentage'),#edit|view
            ('date', 'date'),#edit|view
            ('dropdown', 'dropdown'),#edit|view
            ('file-upload', 'file-upload'),
            ('image-upload', 'image-upload'),
            ('multiple-image-upload', 'multiple-image-upload'),
            ('multiselect-checkbox', 'multiselect-checkbox'),#edit|view
            ('radio', 'radio'),#edit|view
            ('textbox', 'textbox'), #edit|view
            ('textbox-number', 'textbox-number'),#edit|view
            ('blank', 'blank'), #edit|view
        ]
    )
    default_value = models.TextField(max_length=150, null=True, blank=True)
    coordinator_access_level = models.TextField(default='na') #view/edit/na
    technical_engineer_access_level = models.TextField(default='na') #view/edit/na
    valuation_engineer_access_level = models.TextField(default='edit') #view/edit/na
    principal_engineer_access_level = models.TextField(default='edit') #view/edit/na
    formats = models.ManyToManyField('ReportFormat', related_name='supported_fields')

    def get_access_level(self, user):
        if(user.role == "COORDINATOR"):
            return self.coordinator_access_level
        if(user.role == "TECHNICAL_ENGINEER"):
            return self.technical_engineer_access_level
        if(user.role == "VALUATION_ENGINEER"):
            return self.valuation_engineer_access_level
        if(user.role == "PRINCIPLE_ENGINEER"):
            return self.principal_engineer_access_level

        return "NA" #for admin/other non-mentioned roles

    def __str__(self):
        return f"{self.display_name} | {self.section_name} | {self.field_type}"
#     '''
#     fields = ReportFormat.objects.get(pk="land_and_building").supported_fields
#     => gives all fieldManager objects which its linked
#     =>field_names_to_access_levels =  [{field.field_name: {"access_level": field.get_access_level(request.session.user), "value": None}} for field in list(fields)] gives array of field name which are supported
#     for field_name in field_names_to_access_levels.keys():
#         field_names_to_access_levels[value] = get_attribute(site_obj, field_name)
#     '''
class ReportFormat(models.Model):

    # field = models.ForeignKey(FieldManager, related_name='supported_formats')
    format_name = models.TextField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.format_name}"
    

class ApplicationDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='application_details')
    purpose_of_report = models.CharField(
        max_length=40, 
        choices=[
            ('Private Purpose', 'Private Purpose'),
            ('For Bank', 'For Bank'),
            ('Visa Purpose', 'Visa Purpose'),
            ('Education Loan', 'Education Loan')
        ]
    )
    bank_name = models.CharField(
        max_length=100, 
        choices=[
            ('State Bank of India', 'State Bank of India'),
            ('Bank of India', 'Bank of India'),
            ("The Rander People's Co-Operative Bank Ltd.", "The Rander People's Co-Operative Bank Ltd."),
            ('UCO Bank', 'UCO Bank'),
            ('The Mehsana Urban Co-operative Bank Ltd.', 'The Mehsana Urban Co-operative Bank Ltd.')
        ]
    )
    property_type = models.CharField(
        max_length=100, 
        choices=[
            ('N.A. Residential Plot', 'N.A. Residential Plot'),
            ('Residential Bunglow', 'Residential Bunglow'),
            ('Residential Tenament', 'Residential Tenament'),
            ('N.A Land with Allied Civil Construction', 'N.A Land with Allied Civil Construction'),
            ('Residential Row House', 'Residential Row House'),
            ('Commercial Shop / Godown Premises', 'Commercial Shop / Godown Premises'),
            ('Industrial Shed Premises', 'Industrial Shed Premises'),
            ('N.A. Industrial Plot', 'N.A. Industrial Plot')
        ]
    )
    report_format = models.CharField(
        max_length=100,
        choices=[
            ('NBFC (Bajaj Finance)', 'NBFC (Bajaj Finance)'),
            ('SIDBI', 'SIDBI'),
            ('Form O1', 'Form O1'),
            ('NBFC (Ujjivan)', 'NBFC (Ujjivan)'),
            ('ARKA', 'ARKA'),
            ('Land & Building', 'Land & Building'),
            ('Composite Method', 'Composite Method'),
            ('Land & Building 2.0', 'Land & Building 2.0'),
            ('Composite Method 2.0', 'Composite Method 2.0')
        ]
    )
    visit_required = models.CharField(max_length=10, default="Yes", choices=[('Yes', 'Yes'), ('No', 'No')])
    # technical_engineer = models.CharField(max_length=100)
    # valuation_engineer = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=255)
    bank_contact_person_name = models.CharField(max_length=100)
    bank_contact_person_number = models.CharField(max_length=20)
    file_no = models.CharField(max_length=100)
    name_field_title = models.CharField(
        max_length=50,
        choices=[
            ('Name of Owner', 'Name of Owner'),
            ('Name of Owners', 'Name of Owners'),
            ('Name of Proposed Owner', 'Name of Proposed Owner'),
            ('Name of Proposed Owners', 'Name of Proposed Owners')
        ]
    )
    name_of_applicant = models.CharField(max_length=100)
    loan_type = models.CharField(
        max_length=10,
        choices=[('HL', 'HL'), ('LAP', 'LAP'), ('BT', 'BT')]
    )
    property_owner_legal_name = models.CharField(max_length=255)
    person_met_at_site = models.CharField(max_length=255)
    owner_proposed_seller = models.CharField(max_length=255)
    site_contact_person_name = models.CharField(max_length=100)
    site_contact_person_number = models.CharField(max_length=20)
    developer_name = models.CharField(max_length=255, blank=True, null=True)
    joint_ownership_details = models.TextField(blank=True, null=True)
    date_of_visit = models.DateField(auto_now_add=True)
    date_of_valuation = models.DateField(auto_now_add=True)
    due_date_for_visit = models.DateField(blank=True, null=True)
    purpose_of_valuation = models.TextField()
    property_description = models.TextField()

    def __str__(self):
        return f"Application Details for Site {self.site.id}"

class Documents(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='documents')
    layout_plan_approving_authority = models.CharField(max_length=255)
    layout_plan_approval_no = models.CharField(max_length=100)
    layout_plan_document_copy = models.FileField(upload_to='media/uploads/documents/layout_plans/')
    layout_plan_page_no = models.CharField(max_length=50)
    building_plan_approving_authority = models.CharField(max_length=255)
    building_plan_approval_no = models.CharField(max_length=100)
    building_plan_document_copy = models.FileField(upload_to='media/uploads/documents/building_plans/')
    building_plan_page_no = models.CharField(max_length=50)
    construction_permission_approving_authority = models.CharField(max_length=255)
    construction_permission_approval_no = models.CharField(max_length=100)
    construction_permission_document_copy = models.FileField(upload_to='media/uploads/documents/construction_permissions/')
    construction_permission_page_no = models.CharField(max_length=50)
    bu_permission_approving_authority = models.CharField(max_length=255)
    bu_permission_approval_no = models.CharField(max_length=100)
    bu_permission_document_copy = models.FileField(upload_to='media/uploads/documents/bu_permissions/')
    bu_permission_page_no = models.CharField(max_length=50)
    legal_documents_approving_authority = models.CharField(max_length=255)
    legal_documents_approval_no = models.CharField(max_length=100)
    legal_documents_document_copy = models.FileField(upload_to='media/uploads/documents/legal_documents/')
    legal_documents_page_no = models.CharField(max_length=50)
    date_of_issue_validity = models.DateField(null=True)
    approved_map_issuing_authority = models.CharField(max_length=255)
    genuineness_verified = models.CharField(max_length=10, default="Yes", choices=[('Yes', 'Yes'), ('No', 'No')])
    covered_under_govt_enactments = models.CharField(max_length=10, default="No", choices=[('Yes', 'Yes'), ('No', 'No')])
    agricultural_land_conversion = models.CharField(max_length=255, default='No')
    valuer_comments_on_authenticity = models.CharField(max_length=255, default='No')

    def __str__(self):
        return f"Documents for Site {self.site.id}"

class PropertyDetails(models.Model):
    YES_NO_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
    
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='property_details')
    postal_address = models.CharField(max_length=255)
    legal_address = models.CharField(max_length=255)
    plot_no = models.CharField(max_length=255, default='F.P. No. 80, , Old Survey No. 47 ( Survey No. 141 )')
    unit_no = models.CharField(max_length=255)
    tps_village = models.CharField(max_length=255, default='T.P.S. No. 4 / Jodhpur')
    city_town = models.CharField(max_length=255)
    ward_taluka = models.CharField(max_length=255)
    mandal_district = models.CharField(max_length=255)
    property_pin_code = models.CharField(max_length=20)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    locality_name = models.CharField(max_length=255)
    distance_from_city_centre = models.CharField(max_length=255)
    landmark_nearby = models.CharField(max_length=255)
    address_of_property = models.CharField(max_length=255)
    property_state = models.CharField(max_length=255)
    property_city = models.CharField(max_length=255)
    address_matching = models.CharField(max_length=10, choices=YES_NO_CHOICES)
    jurisdiction_municipal_body = models.CharField(max_length=255)

    def __str__(self):
        return f"Property Details for Site {self.site.id}"
    
class SiteDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='site_details')
    # boundaries = models.TextField()
    # boundaries_extended = models.TextField()
    boundaries_east = models.CharField(max_length=20, blank=True, null=True)
    boundaries_west = models.CharField(max_length=20, blank=True, null=True)
    boundaries_north = models.CharField(max_length=20, blank=True, null=True)
    boundaries_south = models.CharField(max_length=20, blank=True, null=True)
    boundaries_north_east = models.CharField(max_length=20, blank=True, null=True)
    boundaries_north_west = models.CharField(max_length=20, blank=True, null=True)
    boundaries_south_west = models.CharField(max_length=20, blank=True, null=True)
    boundaries_south_east = models.CharField(max_length=20, blank=True, null=True)
    property_identified = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    matching_boundaries = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    plot_demarcated = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    property_occupied_by = models.CharField(max_length=20, choices=[('Self', 'Self'), ('Tenant', 'Tenant'), ('Vacant', 'Vacant'), ('Under Construction', 'Under Construction')])
    occupancy_status = models.CharField(max_length=20, choices=[('SORP', 'SORP'), ('SOCP', 'SOCP'), ('Rented', 'Rented'), ('Vacant', 'Vacant')])
    monthly_rent = models.CharField(max_length=255, blank=True, null=True)
    years_of_occupancy = models.CharField(max_length=255, default='NA')
    tenant_owner_relationship = models.CharField(max_length=255, default='NA')
    floor_no = models.CharField(max_length=255)
    property_holding_type = models.CharField(max_length=20, choices=[('Freehold', 'Freehold'), ('Lease Hold', 'Lease Hold')])
    lease_details = models.TextField(blank=True, null=True)
    marketability = models.CharField(max_length=10, choices=[('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')])
    type_of_area = models.CharField(max_length=20, choices=[('Residential Area', 'Residential Area'), ('Commercial Area', 'Commercial Area'), ('Industrial Area', 'Industrial Area')])
    property_class = models.CharField(max_length=10, choices=[('High', 'High'), ('Middle', 'Middle'), ('Poor', 'Poor')])
    locality_class = models.CharField(max_length=20, choices=[('Urban', 'Urban'), ('Semi Urban', 'Semi Urban'), ('Rural', 'Rural')])
    approach_road_size = models.CharField(max_length=20, choices=[('<5 ft', '<5 ft'), ('5-10 ft', '5-10 ft'), ('10-15 ft', '10-15 ft'), ('>15 ft', '>15 ft')])
    visited_with_representative = models.CharField(max_length=255, default='No')
    classification_of_locality = models.CharField(max_length=30, choices=[('High Class', 'High Class'), ('Upper Middle Class', 'Upper Middle Class'), ('Middle Class', 'Middle Class'), ('Poor Class', 'Poor Class')])
    development_of_surrounding = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')])
    flooding_possibility = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    civic_amenities_feasibility = models.CharField(max_length=20, choices=[('Nearby', 'Nearby'), ('Average Distance', 'Average Distance'), ('Far', 'Far')])
    land_topography = models.TextField()
    land_shape = models.TextField()
    land_use_type = models.CharField(max_length=30, choices=[('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Industrial', 'Industrial'), ('Agricultural', 'Agricultural'), ('Mixed', 'Residential & Commercial Area (Mixed)')])
    usage_restriction = models.TextField(blank=True, null=True)
    town_planning_approval = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    plot_type = models.CharField(max_length=20, choices=[('Corner Plot', 'Corner Plot'), ('Intermittent Plot', 'Intermittent Plot')])
    road_type = models.CharField(max_length=20, choices=[('CC Road', 'CC Road'), ('Bituminous Road', 'Bituminous Road'), ('Kachcha Road', 'Kachcha Road'), ('Not Available', 'Not Available')])
    road_width = models.CharField(max_length=30, choices=[('Less than 20 feet', 'Less than 20 feet'), ('More than 20 ft', 'More than 20 ft'), ('Not Applicable', 'Not Applicable')])
    land_locked = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    water_potentiality = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    underground_sewage = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    power_supply = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    site_advantages = models.TextField(default='Regular shape, Marketable size Located at a developed residential / commercial area, Jahangirpura area, Near to Iscon Cross Road, Olpad Road, Hazira-Sayan Road etc. Located within a compounded residential society with common amenities & facilities etc. Neighbourhood surrounding residential & commercial development, Locality etc.')
    special_remarks = models.TextField(blank=True, null=True, default='NA')

    def __str__(self):
        return f"Site Details for Site {self.site.id}"
    
class NDMAParameters(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='ndma_parameters')
    nature_of_building = models.CharField(max_length=30, choices=[('Residential', 'Residential'), ('Industrial', 'Industrial'), ('Commercial', 'Commercial'), ('Residential + Commercial', 'Residential + Commercial')])
    projected_parts_available = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    roof_type = models.CharField(max_length=255)
    concrete_grade = models.CharField(max_length=255)
    sesmic_zone = models.CharField(max_length=255)
    soil_slope_vulnerable = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    fire_exit = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    plan_aspect_ratio = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    type_of_masonry = models.CharField(max_length=255)
    steel_grade = models.CharField(max_length=255)
    environment_exposure_condition = models.CharField(max_length=255)
    soil_liquefiable = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    flood_prone_area = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    structure_type = models.CharField(max_length=30, choices=[('Load Bearing', 'Load Bearing'), ('RCC', 'RCC'), ('Composite Structure', 'Composite Structure'), ('Others', 'Others')])
    expansion_joints_available = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    mortar_type = models.CharField(max_length=255)
    footing_type = models.CharField(max_length=255)
    coastal_regulatory_zone = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    ground_slope_above_20 = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])

    def __str__(self):
        return f"NDMA Parameters for Site {self.site.id}"
    
class NOApprovedPlanDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='no_approved_plan_details')
    sanctioned_plan_provided = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    layout_plan_details = models.CharField(max_length=255)
    construction_plan_details = models.CharField(max_length=255)
    date_of_sanction = models.DateField(null=True)
    plan_validity = models.CharField(max_length=255)
    approving_authority = models.CharField(max_length=255)
    approved_usages = models.CharField(max_length=255)
    number_of_floors = models.CharField(max_length=5)

    def __str__(self):
        return f"NO Approved Plan Details for Site {self.site.id}"
    
class BuildingDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='building_details')
    type_of_building = models.CharField(max_length=30, choices=[('Residential', 'Residential'), ('Industrial', 'Industrial'), ('Commercial', 'Commercial'), ('Residential + Commercial', 'Residential + Commercial')])
    type_of_construction = models.CharField(max_length=50, choices=[('Load Bearing Structure', 'Load Bearing Structure'), ('RCC Frame Structure', 'RCC Frame Structure'), ('Steel Framed', 'Steel Framed'), ('Brick Masonry', 'Brick Masonry')])
    stage_of_construction = models.CharField(max_length=30, choices=[('Completed', 'Completed'), ('Under Construction', 'Under Construction')])
    extent_of_completion = models.CharField(max_length=255, default='NA')
    nature_and_extent_of_violations = models.CharField(max_length=255, default='NA')
    year_of_construction = models.CharField(max_length=10)
    age_of_building = models.CharField(max_length=10)
    residual_age_of_building = models.CharField(max_length=255, default='50 Years subjected to proper Maintenance')
    number_of_floors_and_height = models.CharField(max_length=255, default='Ground + First + / second floor , Avg 3.2 meter')
    number_of_rooms_living_dining = models.CharField(max_length=10)
    number_of_rooms_bedrooms = models.CharField(max_length=10)
    number_of_rooms_toilets = models.CharField(max_length=10)
    number_of_rooms_kitchen = models.CharField(max_length=10)
    plinth_area_floor_wise = models.CharField(max_length=255)
    condition_exterior = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Normal', 'Normal'), ('Poor', 'Poor')])
    condition_interior = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Normal', 'Normal'), ('Poor', 'Poor')])
    foundation = models.CharField(max_length=20, choices=[('RCC Footing', 'RCC Footing'), ('NA', 'NA')])
    basement = models.CharField(max_length=10, choices=[('RCC', 'RCC'), ('NA', 'NA')])
    superstructure = models.CharField(max_length=20, choices=[('RCC Frame', 'RCC Frame'), ('Steel Frame', 'Steel Frame'), ('NA', 'NA')])
    joinery_doors_windows = models.TextField(default='Door - Wooden, Windows - Wooden / MS grill, Alu. Section glazed / MS grill')
    rcc_work = models.CharField(max_length=20, choices=[('Brick Masonry', 'Brick Masonry'), ('NA', 'NA')])
    plastering = models.CharField(max_length=20, choices=[('Cement Plaster', 'Cement Plaster'), ('NA', 'NA')])
    flooring_skirting_dadoing = models.CharField(max_length=50, choices=[('Vitrified', 'Vitrified'), ('Marble', 'Marble'), ('Kota', 'Kota'), ('RCC Trimix', 'RCC Trimix'), ('NA', 'NA')])
    special_finish = models.CharField(max_length=255, default='NA')
    roofing_weatherproof_course = models.CharField(max_length=255, default='NA')
    drainage = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA'), ('---', '---')])
    building_compound_wall = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA'), ('---', '---')])
    type_of_wiring = models.CharField(max_length=20, choices=[('Concealed', 'Concealed'), ('Open', 'Open'), ('NA', 'NA')])
    class_of_fittings = models.CharField(max_length=20, choices=[('Superior', 'Superior'), ('Ordinary', 'Ordinary'), ('Poor', 'Poor'), ('Standard', 'Standard'), ('NA', 'NA')])
    number_of_light_points = models.CharField(max_length=10, default='----')
    fan_points = models.CharField(max_length=50, default='----')
    spare_plug_points = models.CharField(max_length=50, default='----')
    electrical_installation = models.CharField(max_length=255, default='----')
    number_of_water_closets = models.CharField(max_length=10, default='----')
    number_of_wash_basins = models.CharField(max_length=10, default='----')
    number_of_urinals = models.CharField(max_length=10, default='----')
    water_meter_taps = models.CharField(max_length=10, default='----')
    plumbing_installation = models.CharField(max_length=10, default='----')
    roof_height = models.CharField(max_length=50, default='Average 3 mtr')
    particular_of_item = models.CharField(max_length=50, default='Average 3 mtr')
    nature_of_apartment = models.CharField(max_length=30, choices=[('Residential', 'Residential'), ('Industrial', 'Industrial'), ('Commercial', 'Commercial'), ('Residential + Commercial', 'Residential + Commercial')])
    street_or_road = models.CharField(max_length=255)
    locality_description = models.TextField(default='The site benefits from well-developed surrounding areas for both residential and commercial purposes, with easy access to a range of nearby amenities.')
    building_number_of_floors = models.CharField(max_length=4)
    type_of_structure = models.CharField(max_length=50, choices=[('RCC Frame Structure', 'RCC Frame Structure'), ('Load Bearing Structure', 'Load Bearing Structure'), ('RCC Frame / Load Bearing Composite Structure', 'RCC Frame / Load Bearing Composite Structure')])
    number_of_dwelling_units = models.CharField(max_length=255, default='As per plan')
    quality_of_construction = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')])
    appearance_of_building = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')])
    maintenance_of_building = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')])
    facilities_available = models.CharField(max_length=255, choices = [
                                ("Lift", "Lift"),
                                ("Protected Water Supply", "Protected Water Supply"),
                                ("Underground Sewerage", "Underground Sewerage"),
                                ("Car Parking", "Car Parking"),
                                ("Is compound wall existing?", "Is compound wall existing?"),
                                ("Is pavement laid around the building?", "Is pavement laid around the building?")
                            ])
    floor_of_unit = models.CharField(max_length=255)

    def __str__(self):
        return f"Building Details for Site {self.site.id}"
    
class UnitDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='unit_details')
    roof = models.CharField(max_length=20, choices=[('RCC Slab', 'RCC Slab')])
    flooring = models.CharField(max_length=255, choices=[
            ("Vitrified", "Vitrified"),
            ("Marble", "Marble"),
            ("Kota", "Kota"),
            ("Mosaic", "Mosaic")
        ])
    doors = models.CharField(max_length=255, choices=[
            ("Wooden", "Wooden"),
            ("Aluminium section glazed", "Aluminium section glazed"),
            ("MS Shutter", "MS Shutter"),
            ("MS Gate", "MS Gate"),
            ("Toughened Glass Door", "Toughened Glass Door")
        ])
    windows = models.CharField(max_length=255, choices=[
            ("Wooden", "Wooden"),
            ("Aluminium section glazed", "Aluminium section glazed"),
            ("Glass Window", "Glass Window")
        ])
    fittings = models.CharField(max_length=255, choices=[
            ("Concealed", "Concealed"),
            ("Open", "Open")
        ])
    finishing = models.CharField(max_length=255, default='Cement plaster with wall putty')
    house_tax = models.CharField(max_length=255, default='NA')
    assessment_no = models.CharField(max_length=255, default='NA')
    tax_paid_in_name = models.CharField(max_length=255, default='NA')
    tax_amount = models.CharField(max_length=255, default='NA')
    electricity_service_no = models.CharField(max_length=255, default='NA')
    meter_card_maintenance = models.CharField(max_length=255, default='NA')
    maintenance_of_unit = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')])
    undivided_area = models.CharField(max_length=255)
    floor_space_index = models.CharField(max_length=255)
    posh_classification = models.CharField(max_length=255, choices=[('Posh', 'Posh'), ('I class', 'I class'), ('Medium', 'Medium'), ('Ordinary', 'Ordinary')])
    usage_purpose = models.CharField(max_length=20, choices=[('Commercial', 'Commercial'), ('Residential', 'Residential')])

    def __str__(self):
        return f"Unit Details for Site {self.site.id}"
    
    @property
    def get_floors(self, msg):
        return f"message: {msg}"
    
class Marketability(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='marketability')
    marketability_status = models.TextField(default='Good, as the developed area')

    def __str__(self):
        return f"Marketability for Site {self.site.id}"
    
class AssumptionsRemarks(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='assumptions_remarks')
    qualifications_tir_mitigation = models.CharField(max_length=255, default='NA')
    property_sarfaesi_compliant = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    belongs_to_social_infrastructure = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    land_mortgaged_status = models.CharField(max_length=255, default='NA')
    last_two_transactions = models.CharField(max_length=255, blank=True, null=True)
    relevant_aspects_on_value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Assumptions/Remarks for Site {self.site.id}"
    
class TechnicalDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='technical_details')
    construction_quality = models.CharField(max_length=20, choices=[('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')])
    current_occupant = models.CharField(max_length=20, choices=[('Owner', 'Owner'), ('Tenant', 'Tenant'), ('Vacant', 'Vacant')])
    lift_available = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    number_of_lifts = models.CharField(max_length=10)
    separate_independent_access = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No'), ('NA', 'NA')])
    floor_wise_occupancy = models.TextField()

    def __str__(self):
        return f"Technical Details for Site {self.site.id}"
    
class ValuationDetails(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='valuation_details')
    land_area_documents = models.CharField(max_length=255)
    land_area_plan = models.CharField(max_length=255)
    land_area_site_visit = models.CharField(max_length=255)
    land_square_meter = models.CharField(max_length=255)
    land_square_yard = models.CharField(max_length=255)
    land_square_feet = models.CharField(max_length=255)
    super_land_square_meter = models.CharField(max_length=255)
    super_land_square_yard = models.CharField(max_length=255)
    super_land_square_feet = models.CharField(max_length=255)
    carpet_area_square_meter = models.CharField(max_length=255)
    carpet_area_square_yard = models.CharField(max_length=255)
    carpet_area_square_feet = models.CharField(max_length=255)
    built_up_area_square_meter = models.CharField(max_length=255) #229
    built_up_area_square_yard = models.CharField(max_length=255)
    built_up_area_square_feet = models.CharField(max_length=255)
    super_built_up_area_square_meter = models.CharField(max_length=255)
    super_built_up_area_square_yard = models.CharField(max_length=255)
    super_built_up_area_square_feet = models.CharField(max_length=255)
    guideline_land_rate_provided_for = models.CharField(max_length=20, choices=[('Land', 'Land'), ('Super Land', 'Super Land')])
    guideline_rate_land_square_meter = models.CharField(max_length=255)
    market_land_rate_provided_for = models.CharField(max_length=20, choices=[('Land', 'Land'), ('Super Land', 'Super Land')])
    market_rate_land_square_meter = models.CharField(max_length=255)
    market_rate_land_square_yard = models.CharField(max_length=255)
    market_rate_land_square_feet = models.CharField(max_length=255)
    guideline_construction_rate_square_meter = models.CharField(max_length=255, default='14500')
    guideline_rate_provided_for = models.CharField(max_length=20, choices=[('Carpet', 'Carpet'), ('Built Up', 'Built Up'), ('Super Built Up', 'Super Built Up')])
    guideline_rate_square_meter = models.CharField(max_length=255)
    market_construction_rate_provided_for = models.CharField(max_length=20, choices=[('Carpet', 'Carpet'), ('Built Up', 'Built Up'), ('Super Built Up', 'Super Built Up')])
    construction_rate_square_meter = models.CharField(max_length=255)
    construction_rate_square_yard = models.CharField(max_length=255)
    construction_rate_square_feet = models.CharField(max_length=255)
    composite_rate_provided_for = models.CharField(max_length=20, choices=[('Carpet', 'Carpet'), ('Built Up', 'Built Up'), ('Super Built Up', 'Super Built Up')])
    composite_rate_square_meter = models.CharField(max_length=255)
    composite_rate_square_yard = models.CharField(max_length=255)
    composite_rate_square_feet = models.CharField(max_length=255)
    realizable_value_percentage = models.CharField(max_length=255, default='90')
    distress_value_percentage = models.CharField(max_length=255, default='75')
    depreciation_value_percentage = models.CharField(max_length=255, default='0')
    combined_additional_value = models.CharField(max_length=255, blank=True, null=True)
    book_value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Valuation Details for Site {self.site.id}"
    
class ValuationExtraItems(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='valuation_extra_items')
    portico = models.CharField(max_length=255, default='----')
    ornamental_front_door = models.CharField(max_length=255, default='----')
    sit_out_verandah = models.CharField(max_length=255, default='----')
    overhead_water_tank = models.CharField(max_length=255, default='----')
    extra_steel_gates = models.CharField(max_length=255, default='----')
    combined_value_extra_items = models.CharField(max_length=255, default='----')

    def __str__(self):
        return f"Valuation Extra Items for Site {self.site.id}"
    
class ValuationAmenities(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='valuation_amenities')
    wardrobes = models.CharField(max_length=255, default='----')
    glazed_tiles = models.CharField(max_length=255, default='----')
    extra_sinks_bath_tub = models.CharField(max_length=255, default='----')
    marble_ceramic_flooring = models.CharField(max_length=255, default='----')
    interior_decorations = models.CharField(max_length=255, default='----')
    architectural_elevation = models.CharField(max_length=255, default='----')
    panelling_works = models.CharField(max_length=255, default='----')
    aluminium_works = models.CharField(max_length=255, default='----')
    aluminium_hand_rails = models.CharField(max_length=255, default='----')
    false_ceiling = models.CharField(max_length=255, default='----')
    combined_value_amenities = models.CharField(max_length=255, default='----')

    def __str__(self):
        return f"Valuation Amenities for Site {self.site.id}"
    
class ValuationMiscellaneous(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='valuation_miscellaneous')
    separate_toilet_room = models.CharField(max_length=255, default='----')
    separate_lumber_room = models.CharField(max_length=255, default='----')
    separate_water_tank_sump = models.CharField(max_length=255, default='----')
    trees_gardening = models.CharField(max_length=255, default='----')
    combined_value_miscellaneous = models.CharField(max_length=255, default='----')

    def __str__(self):
        return f"Valuation Miscellaneous for Site {self.site.id}"
    
class ValuationServices(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='valuation_services')
    water_supply_arrangements = models.CharField(max_length=255, default='----')
    compound_wall = models.CharField(max_length=255, default='----')
    cb_deposits_fittings = models.CharField(max_length=255, default='----')
    pavement = models.CharField(max_length=255, default='----')
    combined_value_services = models.CharField(max_length=255, default='----')

    def __str__(self):
        return f"Valuation Services for Site {self.site.id}"

class PropertyPhotographs(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='property_photographs')
    property_front_view = models.FileField(upload_to='uploads/images/property_front_view/')
    google_earth_photograph = models.FileField(upload_to='uploads/images/google_earth_photograph/')
    property_photographs = models.ManyToManyField(ImageAttachment)

class InvoiceDetails(models.Model):

    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='invoice_details')
    date_of_invoice = models.DateField(null=True)
    charges_amount = models.CharField(max_length=255)
    other_expenses = models.CharField(max_length=255)
    gst_included = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    cgst = models.CharField(max_length=255)
    sgst = models.CharField(max_length=255)
    total_invoice_amount = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Received', 'Received'), ('Delayed', 'Delayed'), ('Cancelled', 'Cancelled')])
    payment_mode = models.CharField(max_length=20, choices=[('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), ('Cheque', 'Cheque'), ('UPI', 'UPI')])

    def __str__(self):
        return f"Invoice Details for Site {self.site.id}"

    @property
    def get_payment_status_color(self):
            payment_status_colors = {
                "Pending": "yellow",
                "Delayed": "orange",
                "Cancelled": "red",
                "Received": "green"
            }
            return payment_status_colors[self.payment_status]
    
def float_or_zero(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def round_to_nearest(value, base=10000):
    return int(base * round(float_or_zero(value) / base))

def inr_format(value):
    value = round(float_or_zero(value))
    if value == 0:
        return "zero"
    words = num2words(value, lang='en_IN').replace(",", "")
    return words.replace(" and ", " ")

class CalculatedFields(models.Model):
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='calculated_fields')

    @property
    def carpet_area_text(self):

        """
        Returns a formatted string representing the carpet area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.carpet_area_square_feet
        area_sqyd = valuation_details.carpet_area_square_yard
        area_sqm = valuation_details.carpet_area_square_meter

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        result = ""
        parts = []

        if area_sqft:
            parts.append(f"{area_sqft} square feet")
        if area_sqyd:
            parts.append(f"{area_sqyd} square yard")
        if area_sqm:
            parts.append(f"{area_sqm} square meter")

        result = " / ".join(parts)
        return result
    
    @property
    def built_up_area_text(self):
        """
        Returns a formatted string representing the built-up area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.built_up_area_square_feet  # [231]
        area_sqyd = valuation_details.built_up_area_square_yard  # [230]
        area_sqm = valuation_details.built_up_area_square_meter  # [229]

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        result = ""

        if area_sqft:
            result += f"{area_sqft} square feet"

        if area_sqyd:
            if result:
                result += f" / {area_sqyd} square yard"
            else:
                result += f"{area_sqyd} square yard"

        if area_sqm:
            if result:
                result += f" / {area_sqm} square meter"
            else:
                result += f"{area_sqm} square meter"

        return result
    
    @property
    def super_built_up_area_text(self):
        """
        Returns a formatted string representing the super built-up area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqm = valuation_details.super_built_up_area_square_meter  # [232]
        area_sqyd = valuation_details.super_built_up_area_square_yard  # [233]
        area_sqft = valuation_details.super_built_up_area_square_feet  # [234]

        if not area_sqm and not area_sqyd and not area_sqft:
            return "Not Provided"

        result = ""

        if area_sqm:
            result += f"{area_sqm} square meter"

        if area_sqyd:
            if result:
                result += f" / {area_sqyd} square yard"
            else:
                result += f"{area_sqyd} square yard"

        if area_sqft:
            if result:
                result += f" / {area_sqft} square feet"
            else:
                result += f"{area_sqft} square feet"

        return result

    @property
    def dimension_of_the_site(self):
        """
        Returns a multi-line string combining Carpet Area, Built-up Area,
        and Super Built-up Area if available. If all are 'Not Provided',
        returns an empty string.
        """
        output = ""

        carpet = self.carpet_area_text  # [297]
        built_up = self.build_up_area_text  # [298]
        super_built_up = self.super_build_up_area_text  # [299]

        if carpet != "Not Provided":
            output += f"Carpet Area : {carpet}\n"

        if built_up != "Not Provided":
            output += f"Built-up Area : {built_up}\n"

        if super_built_up != "Not Provided":
            output += f"Super Built-up Area : {super_built_up}"

        return output.strip()  # removes trailing newline if any

    @property
    def built_up_area_combined_text(self):
        """
        Returns a combined string of Built-up Area and Super Built-up Area if available.
        If both are 'Not Provided', returns an empty string.
        """
        output = ""

        built_up = self.build_up_area_text  # [298]
        super_built_up = self.super_build_up_area_text  # [299]

        if built_up != "Not Provided":
            output += f"Built-up Area : {built_up}\n"

        if super_built_up != "Not Provided":
            output += f"Super Built-up Area : {super_built_up}"

        return output.strip()  # ensures no trailing newline
    
    @property
    def guideline_rate_unit(self):

        return "square meter"
    #571
    @property
    def area_for_guideline_rate(self) -> float:
        val_for = self.site.valuation_details.guideline_rate_provided_for  # [242]

        if val_for == "Built Up":
            if float(self.site.valuation_details.built_up_area_square_meter or 0) > 0:  # [229]
                return float(self.site.valuation_details.built_up_area_square_meter)
            elif float(self.site.valuation_details.built_up_area_square_feet or 0) > 0:  # [231]
                return float(self.site.valuation_details.built_up_area_square_feet) / 10.76
            elif float(self.site.valuation_details.built_up_area_square_yard or 0) > 0:  # [230]
                return float(self.site.valuation_details.built_up_area_square_yard) / 1.196

        elif val_for == "Carpet":
            if float(self.site.valuation_details.carpet_area_square_meter or 0) > 0:  # [226]
                return float(self.site.valuation_details.carpet_area_square_meter)
            elif float(self.site.valuation_details.carpet_area_square_feet or 0) > 0:  # [228]
                return float(self.site.valuation_details.carpet_area_square_feet) / 10.76
            elif float(self.site.valuation_details.carpet_area_square_yard or 0) > 0:  # [227]
                return float(self.site.valuation_details.carpet_area_square_yard) / 1.196

        elif val_for == "Super Built Up":
            if float(self.site.valuation_details.super_built_up_area_square_feet or 0) > 0:  # [234]
                return float(self.site.valuation_details.super_built_up_area_square_feet)
            elif float(self.site.valuation_details.super_built_up_area_square_meter or 0) > 0:  # [232]
                return float(self.site.valuation_details.super_built_up_area_square_meter) / 10.76
            elif float(self.site.valuation_details.super_built_up_area_square_yard or 0) > 0:  # [233]
                return float(self.site.valuation_details.super_built_up_area_square_yard) / 1.196

        return 0.0

    
    @property
    def guideline_rate_per_unit(self):

        return self.site.valuation_details.guideline_rate_square_meter
    
    @property
    def guideline_rate(self):
        if(self.site.application_details.report_format == "Land & Building 2.0"):
            return self.land_guideline_rate + self.building_depreciated_guideline_rate
        return self.area_for_guideline_rate * self.guideline_rate_per_unit
    @property
    def guideline_rate_per_unit(self):  # [243]
        return float_or_zero(self.site.valuation_details.guideline_rate_square_meter)

    @property
    def guideline_construction_rate(self):  # [241]
        return float_or_zero(self.site.valuation_details.guideline_construction_rate_square_meter)

    @property
    def guideline_construction_cost(self):  # [307]
        return self.area_for_guideline_rate * self.guideline_construction_rate

    @property
    def depreciation_on_construction(self):  # [308]
        try:
            return (self.guideline_construction_cost * float_or_zero(self.site.valuation_details.depreciation_value_percentage)) / 100
        except Exception:
            return 0

    @property
    def depreciated_guideline_rate(self):  # [309]
        return self.guideline_rate - self.depreciation_on_construction

    @property
    def guideline_rate_rounded(self):  # [310]
        if(self.site.application_details.report_format == "Land & Building 2.0"):
            return round(self.guideline_rate / 10000) * 10000
        return round_to_nearest(self.depreciated_guideline_rate)

    @property
    def guideline_rate_in_words(self):  # [311]
        return inr_format(self.guideline_rate_rounded)

    @property
    def guideline_rate_final(self):  # [312]
        return f"{self.guideline_rate_rounded}  ( {self.guideline_rate_in_words} )"

    @property
    def additional_value(self):  # [255]
        return float_or_zero(self.site.valuation_details.combined_additional_value)

    @property
    def fmv_unit(self):  # [313]
        v = self.site.valuation_details
        if float_or_zero(v.composite_rate_square_meter) > 0:
            return "square meter"
        elif float_or_zero(v.composite_rate_square_yard) > 0:
            return "square yard"
        elif float_or_zero(v.composite_rate_square_feet) > 0:
            return "square feet"
        return ""

    @property
    def fmv_per_unit(self):  # [315]
        v = self.site.valuation_details
        return (
            float_or_zero(v.composite_rate_square_meter) or
            float_or_zero(v.composite_rate_square_yard) or
            float_or_zero(v.composite_rate_square_feet)
        )

    @property
    def fmv(self):  # [316]
        return self.area_for_fmv * self.fmv_per_unit

    @property
    def fmv_total(self):  # [318]
        if(self.site.application_details.report_format == "Land & Building 2.0"):

            return self.land_fmv + self.building_fmv + self.total_additional_value
        return self.fmv + self.additional_value

    @property
    def fmv_rounded(self):  # [319]
        return round_to_nearest(self.fmv_total)

    @property
    def fmv_in_words(self):  # [320]
        return inr_format(self.fmv_rounded)

    @property
    def fmv_final(self):  # [321]
        return f"{self.fmv_rounded}  ( {self.fmv_in_words} )"

    @property
    def realizable_value_discount(self):  # [322]
        return 100 - float_or_zero(self.site.valuation_details.realizable_value_percentage)

    @property
    def realizable_value(self):  # [323]
        return (self.fmv_total * float_or_zero(self.site.valuation_details.realizable_value_percentage)) / 100

    @property
    def realizable_value_rounded(self):  # [324]
        return round_to_nearest(self.realizable_value)

    @property
    def realizable_value_in_words(self):  # [325]
        return inr_format(self.realizable_value_rounded)

    @property
    def realizable_value_final(self):  # [326]
        return f"{self.realizable_value_rounded}  ( {self.realizable_value_in_words} )"

    @property
    def distress_value(self):  # [327]
        return (self.fmv_total * float_or_zero(self.site.valuation_details.distress_value_percentage)) / 100

    @property
    def distress_value_rounded(self):  # [328]
        return round_to_nearest(self.distress_value)

    @property
    def distress_value_in_words(self):  # [329]
        return inr_format(self.distress_value_rounded)

    @property
    def distress_value_final(self):  # [330]
        return f"{self.distress_value_rounded}  ( {self.distress_value_in_words} )"

    @property
    def insurable_value(self):  # [331]
        if(self.site.application_details.report_format == "Land & Building 2.0"):

            return self.building_fmv_rounded
        return self.area_for_guideline_rate * 10.76 * 1500

    @property
    def insurable_value_rounded(self):  # [332]
        return round_to_nearest(self.insurable_value)

    @property
    def insurable_value_in_words(self):  # [333]
        return inr_format(self.insurable_value_rounded)

    @property
    def insurable_value_final(self):  # [334]
        return f"{self.insurable_value_rounded}  ( {self.insurable_value_in_words} )"

    @property
    def book_value_in_words(self):  # [256]
        return inr_format(float_or_zero(self.site.valuation_details.book_value))

    @property
    def guideline_rate_per_unit_old(self):  # [243]
        return float_or_zero(self.site.valuation_details.guideline_rate_square_meter) / 1.8
    @property
    def area_for_fmv(self):

        

        vd = self.site.valuation_details  # avoid repeated DB hits
        unit = self.fmv_unit
        val_for = vd.composite_rate_provided_for

        def get_value(*values):
            for v in values:
                try:
                    val = float(v)
                    if val > 0:
                        return val
                except (ValueError, TypeError):
                    continue
            return 0

        if val_for == "Carpet":
            if unit == "square_yard":
                return get_value(
                    vd.carpet_area_square_yard,
                    float_or_zero(vd.carpet_area_square_meter) * 1.196,
                    float_or_zero(vd.carpet_area_square_feet) / 9
                )
            elif unit == "square_meter":
                return get_value(
                    vd.carpet_area_square_meter,
                    float_or_zero(vd.carpet_area_square_yard) / 1.196,
                    float_or_zero(vd.carpet_area_square_feet) / 10.76
                )
            elif unit == "square_feet":
                return get_value(
                    vd.carpet_area_square_feet,
                    float_or_zero(vd.carpet_area_square_meter) * 10.76,
                    float_or_zero(vd.carpet_area_square_yard) * 9
                )

        elif val_for == "Built Up":
            if unit == "square_yard":
                return get_value(
                    vd.built_up_area_square_yard,
                    float_or_zero(vd.built_up_area_square_meter) * 1.196,
                    float_or_zero(vd.built_up_area_square_feet) / 9
                )
            elif unit == "square_meter":
                return get_value(
                    vd.built_up_area_square_meter,
                    float_or_zero(vd.built_up_area_square_yard) / 1.196,
                    float_or_zero(vd.built_up_area_square_feet) / 10.76
                )
            elif unit == "square_feet":
                return get_value(
                    vd.built_up_area_square_feet,
                    float_or_zero(vd.built_up_area_square_meter) * 10.76,
                    float_or_zero(vd.built_up_area_square_yard) * 9
                )

        elif val_for == "Super Built Up":
            if unit == "square_yard":
                return get_value(
                    vd.super_built_up_area_square_yard,
                    float_or_zero(vd.super_built_up_area_square_feet) * 1.196,
                    float_or_zero(vd.super_built_up_area_square_meter) / 9
                )
            elif unit == "square_meter":
                return get_value(
                    vd.super_built_up_area_square_feet,
                    float_or_zero(vd.super_built_up_area_square_yard) / 1.196,
                    float_or_zero(vd.super_built_up_area_square_meter) / 10.76
                )
            elif unit == "square_feet":
                return get_value(
                    vd.super_built_up_area_square_feet,
                    float_or_zero(vd.super_built_up_area_square_meter) * 10.76,
                    float_or_zero(vd.super_built_up_area_square_yard) * 9
                )

        return 0 
    


    # LAND AND BUILDING SPECIFICS
    @property
    def land_area_text(self):
        """
        Returns a formatted string representing the land area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.land_square_feet
        area_sqyd = valuation_details.land_square_yard
        area_sqm = valuation_details.land_square_meter

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        result = ""
        parts = []

        if area_sqft:
            parts.append(f"{area_sqft} square feet")
        if area_sqyd:
            parts.append(f"{area_sqyd} square yard")
        if area_sqm:
            parts.append(f"{area_sqm} square meter")

        result = " / ".join(parts)
        return result

    @property
    def super_land_area_text(self):
        """
        Returns a formatted string representing the super land area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.super_land_square_feet
        area_sqyd = valuation_details.super_land_square_yard
        area_sqm = valuation_details.super_land_square_meter

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        result = ""
        parts = []

        if area_sqft:
            parts.append(f"{area_sqft} square feet")
        if area_sqyd:
            parts.append(f"{area_sqyd} square yard")
        if area_sqm:
            parts.append(f"{area_sqm} square meter")

        result = " / ".join(parts)
        return result

    @property
    def total_land_text(self):
        """
        Returns combined land area text with proper formatting.
        """
        result = ""
        
        if self.land_area_text != "Not Provided":
            result += f"Land Area : {self.land_area_text}\n"
        
        if self.super_land_area_text != "Not Provided":
            result += f"Super Land Area : {self.super_land_area_text}\n"
        
        return result.rstrip('\n')

    @property
    def land_guideline_rate_unit(self):
        """
        Returns the unit for land guideline rate.
        """
        return "square meter"

    @property
    def land_area_for_guideline_rate(self):
        """
        Returns the area to be used for guideline rate calculation.
        """
        valuation_details = self.site.valuation_details
        
        if valuation_details.guideline_land_rate_provided_for == "Land":
            # Return first positive value among land areas
            if valuation_details.land_square_meter and float(valuation_details.land_square_meter or 0) > 0:
                return float(valuation_details.land_square_meter)
            elif valuation_details.land_square_yard and float(valuation_details.land_square_yard or 0) > 0:
                return float(valuation_details.land_square_yard) / 10.76
            elif valuation_details.land_square_feet and float(valuation_details.land_square_feet or 0) > 0:
                return float(valuation_details.land_square_feet) / 1.196
        
        elif valuation_details.guideline_land_rate_provided_for == "Super Land":
            # Return first positive value among super land areas
            if valuation_details.super_land_square_meter and float(valuation_details.super_land_square_meter or 0) > 0:
                return float(valuation_details.super_land_square_meter)
            elif valuation_details.super_land_square_yard and float(valuation_details.super_land_square_yard or 0) > 0:
                return float(valuation_details.super_land_square_yard) / 10.76
            elif valuation_details.super_land_square_feet and float(valuation_details.super_land_square_feet or 0) > 0:
                return float(valuation_details.super_land_square_feet) / 1.196
        
        return 0

    @property
    def land_guideline_rate_per_unit(self):
        """
        Returns the guideline rate per unit for land.
        """
        valuation_details = self.site.valuation_details
        return float(valuation_details.guideline_rate_land_square_meter or 0)

    @property
    def land_guideline_rate(self):
        """
        Calculates the total land guideline rate.
        """
        return self.land_area_for_guideline_rate * self.land_guideline_rate_per_unit

    @property
    def land_guideline_rate_rounded(self):
        """
        Returns the land guideline rate rounded to nearest 10,000.
        """
        return round(self.land_guideline_rate / 10000) * 10000

    @property
    def land_guideline_rate_in_words(self):
        """
        Converts the rounded land guideline rate to Indian Rupees words.
        """
        # You'll need to implement INR conversion function
        return inr_format(self.land_guideline_rate_rounded)

    @property
    def land_guideline_rate_final(self):
        """
        Returns the final formatted land guideline rate with amount in words.
        """
        return f"{self.land_guideline_rate_rounded} ( {self.land_guideline_rate_in_words} )"

    @property
    def building_guideline_rate_unit(self):
        """
        Returns the unit for building guideline rate.
        """
        return "square meter"

    @property
    def building_area_for_guideline_rate(self):
        """
        Returns the building area to be used for guideline rate calculation.
        """
        valuation_details = self.site.valuation_details
        rate_provided_for = valuation_details.guideline_rate_provided_for
        
        if rate_provided_for == "Built Up":
            if valuation_details.built_up_area_square_meter and float(valuation_details.built_up_area_square_meter or 0) > 0:
                return float(valuation_details.built_up_area_square_meter)
            elif valuation_details.built_up_area_square_feet and float(valuation_details.built_up_area_square_feet or 0) > 0:
                return float(valuation_details.built_up_area_square_feet) / 1.196
            elif valuation_details.built_up_area_square_yard and float(valuation_details.built_up_area_square_yard or 0) > 0:
                return float(valuation_details.built_up_area_square_yard) / 10.76
        
        elif rate_provided_for == "Carpet":
            if valuation_details.carpet_area_square_meter and float(valuation_details.carpet_area_square_meter or 0) > 0:
                return float(valuation_details.carpet_area_square_meter)
            elif valuation_details.carpet_area_square_feet and float(valuation_details.carpet_area_square_feet or 0) > 0:
                return float(valuation_details.carpet_area_square_feet) / 1.196
            elif valuation_details.carpet_area_square_yard and float(valuation_details.carpet_area_square_yard or 0) > 0:
                return float(valuation_details.carpet_area_square_yard) / 10.76
        
        elif rate_provided_for == "Super Built Up":
            if valuation_details.super_built_up_area_square_meter and float(valuation_details.super_built_up_area_square_meter or 0) > 0:
                return float(valuation_details.super_built_up_area_square_meter)
            elif valuation_details.super_built_up_area_square_feet and float(valuation_details.super_built_up_area_square_feet or 0) > 0:
                return float(valuation_details.super_built_up_area_square_feet) / 1.196
            elif valuation_details.super_built_up_area_square_yard and float(valuation_details.super_built_up_area_square_yard or 0) > 0:
                return float(valuation_details.super_built_up_area_square_yard) / 10.76
        
        return 0

    @property
    def building_guideline_construction_rate(self):
        """
        Returns the guideline construction rate.
        """
        valuation_details = self.site.valuation_details
        return float(valuation_details.guideline_construction_rate_square_meter or 0)

    @property
    def building_guideline_construction_cost(self):
        """
        Calculates the building guideline construction cost.
        """
        return self.building_guideline_construction_rate * self.building_area_for_guideline_rate

    @property
    def building_depreciation_on_construction(self):
        """
        Calculates depreciation on construction.
        """
        try:
            valuation_details = self.site.valuation_details
            depreciation_percent = float(valuation_details.depreciation_value_percentage or 0)
            return (self.building_guideline_construction_cost * depreciation_percent) / 100
        except:
            return 0

    @property
    def building_depreciated_guideline_rate(self):
        """
        Calculates the depreciated guideline rate for building.
        """
        return self.building_guideline_construction_cost - self.building_depreciation_on_construction
    
    @property
    def land_fmv_unit(self):
        """
        Returns the unit for land FMV calculation.
        """
        valuation_details = self.site.valuation_details
        
        if valuation_details.market_rate_land_square_meter and float(valuation_details.market_rate_land_square_meter or 0) > 0:
            return "square meter"
        elif valuation_details.market_rate_land_square_yard and float(valuation_details.market_rate_land_square_yard or 0) > 0:
            return "square yard"
        elif valuation_details.market_rate_land_square_feet and float(valuation_details.market_rate_land_square_feet or 0) > 0:
            return "square feet"
        
        return "square meter"

    @property
    def land_area_for_fmv(self):
        """
        Returns the land area to be used for FMV calculation.
        """
        valuation_details = self.site.valuation_details
        market_rate_for = valuation_details.market_land_rate_provided_for
        unit = self.land_fmv_unit
        
        if market_rate_for == "Land":
            if unit == "square yard":
                if valuation_details.land_square_yard and float(valuation_details.land_square_yard or 0) > 0:
                    return float(valuation_details.land_square_yard)
                elif valuation_details.land_square_meter and float(valuation_details.land_square_meter or 0) > 0:
                    return float(valuation_details.land_square_meter) * 1.196
                elif valuation_details.land_square_feet and float(valuation_details.land_square_feet or 0) > 0:
                    return float(valuation_details.land_square_feet) / 9
            elif unit == "square meter":
                if valuation_details.land_square_meter and float(valuation_details.land_square_meter or 0) > 0:
                    return float(valuation_details.land_square_meter)
                elif valuation_details.land_square_yard and float(valuation_details.land_square_yard or 0) > 0:
                    return float(valuation_details.land_square_yard) / 1.196
                elif valuation_details.land_square_feet and float(valuation_details.land_square_feet or 0) > 0:
                    return float(valuation_details.land_square_feet) / 10.76
            elif unit == "square feet":
                if valuation_details.land_square_feet and float(valuation_details.land_square_feet or 0) > 0:
                    return float(valuation_details.land_square_feet)
                elif valuation_details.land_square_meter and float(valuation_details.land_square_meter or 0) > 0:
                    return float(valuation_details.land_square_meter) * 10.76
                elif valuation_details.land_square_yard and float(valuation_details.land_square_yard or 0) > 0:
                    return float(valuation_details.land_square_yard) * 9
        
        elif market_rate_for == "Super Land":
            if unit == "square yard":
                if valuation_details.super_land_square_yard and float(valuation_details.super_land_square_yard or 0) > 0:
                    return float(valuation_details.super_land_square_yard)
                elif valuation_details.super_land_square_meter and float(valuation_details.super_land_square_meter or 0) > 0:
                    return float(valuation_details.super_land_square_meter) * 1.196
                elif valuation_details.super_land_square_feet and float(valuation_details.super_land_square_feet or 0) > 0:
                    return float(valuation_details.super_land_square_feet) / 9
            elif unit == "square meter":
                if valuation_details.super_land_square_meter and float(valuation_details.super_land_square_meter or 0) > 0:
                    return float(valuation_details.super_land_square_meter)
                elif valuation_details.super_land_square_yard and float(valuation_details.super_land_square_yard or 0) > 0:
                    return float(valuation_details.super_land_square_yard) / 1.196
                elif valuation_details.super_land_square_feet and float(valuation_details.super_land_square_feet or 0) > 0:
                    return float(valuation_details.super_land_square_feet) / 10.76
            elif unit == "square feet":
                if valuation_details.super_land_square_feet and float(valuation_details.super_land_square_feet or 0) > 0:
                    return float(valuation_details.super_land_square_feet)
                elif valuation_details.super_land_square_meter and float(valuation_details.super_land_square_meter or 0) > 0:
                    return float(valuation_details.super_land_square_meter) * 10.76
                elif valuation_details.super_land_square_yard and float(valuation_details.super_land_square_yard or 0) > 0:
                    return float(valuation_details.super_land_square_yard) * 9
        
        return 0

    @property
    def land_fmv_per_unit(self):
        """
        Returns the land FMV rate per unit.
        """
        valuation_details = self.site.valuation_details
        unit = self.land_fmv_unit
        
        if unit == "square meter":
            return float(valuation_details.market_rate_land_square_meter or 0)
        elif unit == "square yard":
            return float(valuation_details.market_rate_land_square_yard or 0)
        elif unit == "square feet":
            return float(valuation_details.market_rate_land_square_feet or 0)
        
        return 0

    @property
    def land_fmv(self):
        """
        Calculates the land FMV.
        """
        return self.land_area_for_fmv * self.land_fmv_per_unit

    @property
    def land_fmv_rounded(self):
        """
        Returns the land FMV rounded to nearest 10,000.
        """
        return round(self.land_fmv / 10000) * 10000

    @property
    def land_fmv_in_words(self):
        """
        Converts the rounded land FMV to Indian Rupees words.
        """
        return inr_format(self.land_fmv_rounded)

    @property
    def land_fmv_final(self):
        """
        Returns the final formatted land FMV with amount in words.
        """
        return f"{self.land_fmv_rounded} ( {self.land_fmv_in_words} )"

    @property
    def building_carpet_area_text(self):
        """
        Returns a formatted string representing the carpet area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.carpet_area_square_feet
        area_sqyd = valuation_details.carpet_area_square_yard
        area_sqm = valuation_details.carpet_area_square_meter

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        parts = []

        if area_sqft:
            parts.append(f"{area_sqft} square feet")
        if area_sqyd:
            parts.append(f"{area_sqyd} square yard")
        if area_sqm:
            parts.append(f"{area_sqm} square meter")

        return " / ".join(parts)

    @property
    def building_built_up_area_text(self):
        """
        Returns a formatted string representing the built-up area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.built_up_area_square_feet
        area_sqyd = valuation_details.built_up_area_square_yard
        area_sqm = valuation_details.built_up_area_square_meter

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        parts = []

        if area_sqft:
            parts.append(f"{area_sqft} square feet")
        if area_sqyd:
            parts.append(f"{area_sqyd} square yard")
        if area_sqm:
            parts.append(f"{area_sqm} square meter")

        return " / ".join(parts)

    @property
    def building_super_built_up_area_text(self):
        """
        Returns a formatted string representing the super built-up area in available units.
        If all inputs are empty or None, returns 'Not Provided'.
        """
        valuation_details = self.site.valuation_details
        area_sqft = valuation_details.super_built_up_area_square_feet
        area_sqyd = valuation_details.super_built_up_area_square_yard
        area_sqm = valuation_details.super_built_up_area_square_meter

        if not area_sqft and not area_sqyd and not area_sqm:
            return "Not Provided"

        parts = []

        if area_sqft:
            parts.append(f"{area_sqft} square feet")
        if area_sqyd:
            parts.append(f"{area_sqyd} square yard")
        if area_sqm:
            parts.append(f"{area_sqm} square meter")

        return " / ".join(parts)

    @property
    def total_building_area_text(self):
        """
        Returns combined building area text with proper formatting.
        """
        result = ""
        
        if self.building_carpet_area_text != "Not Provided":
            result += f"Carpet Area : {self.building_carpet_area_text}\n"
        
        if self.building_built_up_area_text != "Not Provided":
            result += f"Built-up Area : {self.building_built_up_area_text}\n"
        
        if self.building_super_built_up_area_text != "Not Provided":
            result += f"Super Built-up Area : {self.building_super_built_up_area_text}"
        
        return result.rstrip('\n')

    @property
    def building_fmv_unit(self):
        """
        Returns the unit for building FMV calculation.
        """
        valuation_details = self.site.valuation_details
        
        if valuation_details.construction_rate_square_meter and float(valuation_details.construction_rate_square_meter or 0) > 0:
            return "square meter"
        elif valuation_details.construction_rate_square_yard and float(valuation_details.construction_rate_square_yard or 0) > 0:
            return "square yard"
        elif valuation_details.construction_rate_square_feet and float(valuation_details.construction_rate_square_feet or 0) > 0:
            return "square feet"
        
        return "square meter"

    @property
    def building_area_for_fmv(self):
        """
        Returns the building area to be used for FMV calculation.
        """
        valuation_details = self.site.valuation_details
        rate_provided_for = valuation_details.market_construction_rate_provided_for
        unit = self.building_fmv_unit
        
        if rate_provided_for == "Carpet":
            if unit == "square yard":
                if valuation_details.carpet_area_square_yard and float(valuation_details.carpet_area_square_yard or 0) > 0:
                    return float(valuation_details.carpet_area_square_yard)
                elif valuation_details.carpet_area_square_meter and float(valuation_details.carpet_area_square_meter or 0) > 0:
                    return float(valuation_details.carpet_area_square_meter) * 1.196
                elif valuation_details.carpet_area_square_feet and float(valuation_details.carpet_area_square_feet or 0) > 0:
                    return float(valuation_details.carpet_area_square_feet) / 9
            elif unit == "square meter":
                if valuation_details.carpet_area_square_meter and float(valuation_details.carpet_area_square_meter or 0) > 0:
                    return float(valuation_details.carpet_area_square_meter)
                elif valuation_details.carpet_area_square_yard and float(valuation_details.carpet_area_square_yard or 0) > 0:
                    return float(valuation_details.carpet_area_square_yard) / 1.196
                elif valuation_details.carpet_area_square_feet and float(valuation_details.carpet_area_square_feet or 0) > 0:
                    return float(valuation_details.carpet_area_square_feet) / 10.76
            elif unit == "square feet":
                if valuation_details.carpet_area_square_feet and float(valuation_details.carpet_area_square_feet or 0) > 0:
                    return float(valuation_details.carpet_area_square_feet)
                elif valuation_details.carpet_area_square_meter and float(valuation_details.carpet_area_square_meter or 0) > 0:
                    return float(valuation_details.carpet_area_square_meter) * 10.76
                elif valuation_details.carpet_area_square_yard and float(valuation_details.carpet_area_square_yard or 0) > 0:
                    return float(valuation_details.carpet_area_square_yard) * 9
        
        elif rate_provided_for == "Built Up":
            if unit == "square yard":
                if valuation_details.built_up_area_square_yard and float(valuation_details.built_up_area_square_yard or 0) > 0:
                    return float(valuation_details.built_up_area_square_yard)
                elif valuation_details.built_up_area_square_meter and float(valuation_details.built_up_area_square_meter or 0) > 0:
                    return float(valuation_details.built_up_area_square_meter) * 1.196
                elif valuation_details.built_up_area_square_feet and float(valuation_details.built_up_area_square_feet or 0) > 0:
                    return float(valuation_details.built_up_area_square_feet) / 9
            elif unit == "square meter":
                if valuation_details.built_up_area_square_meter and float(valuation_details.built_up_area_square_meter or 0) > 0:
                    return float(valuation_details.built_up_area_square_meter)
                elif valuation_details.built_up_area_square_yard and float(valuation_details.built_up_area_square_yard or 0) > 0:
                    return float(valuation_details.built_up_area_square_yard) / 1.196
                elif valuation_details.built_up_area_square_feet and float(valuation_details.built_up_area_square_feet or 0) > 0:
                    return float(valuation_details.built_up_area_square_feet) / 10.76
            elif unit == "square feet":
                if valuation_details.built_up_area_square_feet and float(valuation_details.built_up_area_square_feet or 0) > 0:
                    return float(valuation_details.built_up_area_square_feet)
                elif valuation_details.built_up_area_square_meter and float(valuation_details.built_up_area_square_meter or 0) > 0:
                    return float(valuation_details.built_up_area_square_meter) * 10.76
                elif valuation_details.built_up_area_square_yard and float(valuation_details.built_up_area_square_yard or 0) > 0:
                    return float(valuation_details.built_up_area_square_yard) * 9
        
        elif rate_provided_for == "Super Built Up":
            if unit == "square yard":
                if valuation_details.super_built_up_area_square_yard and float(valuation_details.super_built_up_area_square_yard or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_yard)
                elif valuation_details.super_built_up_area_square_meter and float(valuation_details.super_built_up_area_square_meter or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_meter) * 1.196
                elif valuation_details.super_built_up_area_square_feet and float(valuation_details.super_built_up_area_square_feet or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_feet) / 9
            elif unit == "square meter":
                if valuation_details.super_built_up_area_square_meter and float(valuation_details.super_built_up_area_square_meter or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_meter)
                elif valuation_details.super_built_up_area_square_yard and float(valuation_details.super_built_up_area_square_yard or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_yard) / 1.196
                elif valuation_details.super_built_up_area_square_feet and float(valuation_details.super_built_up_area_square_feet or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_feet) / 10.76
            elif unit == "square feet":
                if valuation_details.super_built_up_area_square_feet and float(valuation_details.super_built_up_area_square_feet or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_feet)
                elif valuation_details.super_built_up_area_square_meter and float(valuation_details.super_built_up_area_square_meter or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_meter) * 10.76
                elif valuation_details.super_built_up_area_square_yard and float(valuation_details.super_built_up_area_square_yard or 0) > 0:
                    return float(valuation_details.super_built_up_area_square_yard) * 9
        
        return 0

    @property
    def building_fmv_per_unit(self):
        """
        Returns the building FMV rate per unit.
        """
        valuation_details = self.site.valuation_details
        
        if valuation_details.construction_rate_square_meter and float(valuation_details.construction_rate_square_meter or 0) > 0:
            return float(valuation_details.construction_rate_square_meter)
        elif valuation_details.construction_rate_square_yard and float(valuation_details.construction_rate_square_yard or 0) > 0:
            return float(valuation_details.construction_rate_square_yard)
        elif valuation_details.construction_rate_square_feet and float(valuation_details.construction_rate_square_feet or 0) > 0:
            return float(valuation_details.construction_rate_square_feet)
        
        return 0

    @property
    def building_estimated_fmv(self):
        """
        Calculates the estimated building FMV.
        """
        return self.building_area_for_fmv * self.building_fmv_per_unit

    @property
    def building_depreciation_percentage(self):
        """
        Returns the depreciation percentage as decimal.
        """
        valuation_details = self.site.valuation_details
        return float(valuation_details.depreciation_value_percentage or 0) / 100
    
    @property
    def building_depreciation(self):
        """
        Calculates the building depreciation amount.
        """
        return self.building_estimated_fmv * self.building_depreciation_percentage

    @property
    def building_fmv(self):
        """
        Calculates the building FMV after depreciation.
        """
        return self.building_estimated_fmv - self.building_depreciation

    @property
    def building_fmv_rounded(self):
        """
        Returns the building FMV rounded to nearest 10,000.
        """
        return round(self.building_fmv / 10000) * 10000

    @property
    def building_fmv_in_words(self):
        """
        Converts the rounded building FMV to Indian Rupees words.
        """
        return inr_format(self.building_fmv_rounded)

    @property
    def building_fmv_final(self):
        """
        Returns the final formatted building FMV with amount in words.
        """
        return f"{self.building_fmv_rounded} ( {self.building_fmv_in_words} )"

    @property
    def total_additional_value(self):
        """
        Returns the additional value.
        """
        valuation_details = self.site.valuation_details
        return float(valuation_details.combined_additional_value or 0)

    @property
    def fmv_total(self):
        """
        Calculates the total FMV (Land + Building + Additional Value).
        """
        return self.land_fmv + self.building_fmv + self.total_additional_value

    @property
    def fmv_rounded(self):
        """
        Returns the total FMV rounded to nearest 10,000.
        """
        return round(self.fmv_total / 10000) * 10000

    @property
    def fmv_in_words(self):
        """
        Converts the rounded total FMV to Indian Rupees words.
        """
        return inr_format(self.fmv_rounded)

    @property
    def fmv_final(self):
        """
        Returns the final formatted total FMV with amount in words.
        """
        return f"{self.fmv_rounded} ( {self.fmv_in_words} )"

    @property
    def realizable_value_discount(self):
        """
        Calculates the realizable value discount percentage.
        """
        valuation_details = self.site.valuation_details
        realizable_percentage = float(valuation_details.realizable_value_percentage or 90)
        return 100 - realizable_percentage

    @property
    def realizable_value(self):
        """
        Calculates the realizable value.
        """
        valuation_details = self.site.valuation_details
        realizable_percentage = float(valuation_details.realizable_value_percentage or 90)
        return self.fmv_total * realizable_percentage / 100

    @property
    def realizable_value_rounded(self):
        """
        Returns the realizable value rounded to nearest 10,000.
        """
        return round(self.realizable_value / 10000) * 10000

    @property
    def realizable_value_in_words(self):
        """
        Converts the rounded realizable value to Indian Rupees words.
        """
        return inr_format(self.realizable_value_rounded)

    @property
    def realizable_value_final(self):
        """
        Returns the final formatted realizable value with amount in words.
        """
        return f"{self.realizable_value_rounded} ( {self.realizable_value_in_words} )"

    @property
    def distress_value(self):
        """
        Calculates the distress value.
        """
        valuation_details = self.site.valuation_details
        distress_percentage = float(valuation_details.distress_value_percentage or 75)
        return self.fmv_total * distress_percentage / 100

    @property
    def distress_value_rounded(self):
        """
        Returns the distress value rounded to nearest 10,000.
        """
        return round(self.distress_value / 10000) * 10000

    @property
    def distress_value_in_words(self):
        """
        Converts the rounded distress value to Indian Rupees words.
        """
        return inr_format(self.distress_value_rounded)

    @property
    def distress_value_final(self):
        """
        Returns the final formatted distress value with amount in words.
        """
        return f"{self.distress_value_rounded} ( {self.distress_value_in_words} )"

    @property
    def insurable_value(self):
        """
        Returns the insurable value (equal to building FMV rounded).
        """
        return self.building_fmv_rounded

    @property
    def insurable_value_rounded(self):
        """
        Returns the insurable value rounded to nearest 10,000.
        """
        return round(self.insurable_value / 10000) * 10000

    @property
    def insurable_value_in_words(self):
        """
        Converts the rounded insurable value to Indian Rupees words.
        """
        return inr_format(self.insurable_value_rounded)

    @property
    def insurable_value_final(self):
        """
        Returns the final formatted insurable value with amount in words.
        """
        return f"{self.insurable_value_rounded} ( {self.insurable_value_in_words} )"

    @property
    def book_value_in_words(self):
        """
        Converts the book value to Indian Rupees words.
        """
        valuation_details = self.site.valuation_details
        book_value = float(valuation_details.book_value or 0)
        return inr_format(book_value)

    @property
    def land_guideline_rate_per_unit_old(self):
        """
        Returns half of the guideline rate per unit for land (old calculation).
        """
        return self.land_guideline_rate_per_unit / 2
'''

from django.db import models
from num2words import num2words

def float_or_zero(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def round_to_nearest(value, base=10000):
    return int(base * round(float_or_zero(value) / base))

def inr_format(value):
    value = round(float_or_zero(value))
    if value == 0:
        return "zero"
    words = num2words(value, lang='en_IN').replace(",", "")
    return words.replace(" and ", " ")

class ComputedValuationMixin:


'''