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
    built_up_area_square_meter = models.CharField(max_length=255)
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