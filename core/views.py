from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import CustomUser, Site, Document, Comment, ReportFormat
from datetime import datetime
from django.core.signing import Signer
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

@login_required
def home(request):

    sites = []

    if(request.method == 'GET'):
        if(request.GET.get("filter_status", False)):
            filter_statuses = request.GET.get("filter_status").split(",")
            report_statuses = [status.replace("-", "_").upper() for status in filter_statuses if "payment" not in status]
            payment_statuses = [status.replace("payment-", "").upper() for status in filter_statuses if "payment" in status]

            if(report_statuses):
                report_status_filtered_sites = Site.objects.filter(report_status__in=report_statuses)
                sites = report_status_filtered_sites
                
            if(payment_statuses):
                payment_status_filtered_sites = Site.objects.filter(payment_status__in=payment_statuses)
                if(len(sites) > 0):
                    sites = sites | payment_status_filtered_sites
                else:
                    sites = payment_status_filtered_sites

        if(request.GET.get("filter_search_query", False)):
            s = request.GET.get("filter_search_query")
            if(len(sites) == 0):
                sites = Site.objects.all()
            sites = sites.filter(name__contains=s)

            # if(len(sites) > 0):
                # sites = sites.filter(naesearch_filtered_sites

            print("Filtered sites: ", sites)
        if((not request.GET.get("filter_search_query", False)) and (not request.GET.get("filter_status", False))):
            sites = Site.objects.all()

        if(request.GET.get("newest", False)):
            if(len(sites) > 0):
                sites = sites.order_by('-created_on')
            
        paginator = Paginator(sites, 10)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'home.html', context={"sites": page_obj })

    else:

        print(request.GET)

        return render(request, 'home.html')



def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)  # Use 'username' if using default user model
        
        if user is not None:
            auth_login(request, user)
            # messages.success(request, "Login successful!")
            return redirect('home')  # Change to your desired redirect URL
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login/')
def register_site(request):
    
    if request.user.role != CustomUser.Roles.COORDINATOR:

        messages.error(request, f"Only {CustomUser.Roles.COORDINATOR} can access this page.")

        return render(request, 'message_display.html')
    
    else:

        return render(request, 'register_site.html')
    
@api_view(['POST'])
@parser_classes([MultiPartParser])
def register_site_form(request):

    # try:

        # print("asd::",request.data['file'])
        # print("asd::",type(request.data['file']))
        # print("asd::",request.data)
        # print("asd::",type(request.data['attachments']))
    request.data._mutable = True
    files = request.FILES
    comment = request.data['comment']
    data = request.POST.copy()
    del data['comment']
    
    del data['visit_due_date']
    with transaction.atomic():
        print(type(data))
        print(type(data['bank_contact_person_name']))
        site = Site.objects.create(
            name=data["name"],
            bank_contact_person_name=data["bank_contact_person_name"],
            bank_contact_person_number=data["bank_contact_person_number"],
            property_contact_person_name=data["property_contact_person_name"],
            property_contact_person_number=data["property_contact_person_number"],
            visit_due_date=datetime.strptime('-'.join(request.data['visit_due_date'].split('/')[::-1]), "%Y-%d-%m").date(),
            name_field_title=data["name_field_title"],
            name_field_value=data["name_field_value"],
            intended_purchaser_name=data["intended_purchaser_name"],
            property_location=data["property_location"],
            branch_name_address=data["branch_name_address"],
            borrowal_unit=data["borrowal_unit"],
            customer_details_name=data["customer_details_name"],
            customer_details_application_number=data["customer_details_application_number"],
            property_details_address=data["property_details_address"]
        )
        # site.visit_due_date = datetime.strptime('-'.join(request.data['visit_due_date'].split('/')[::-1]), "%Y-%d-%m").date()
        site.save()
        print(request.data.getlist('file'))
        print(type(request.FILES))
        print("---------")
        for file in request.data.getlist('file'):
            print("here, ", file)
            _ = Document.objects.create(site=site, attachment=file).save()

        if(comment):
            _ = Comment.objects.create(site=site, author=request.user, comment=comment).save()


        print("SUCCESS", request.data)


    return Response(status=200,data={"message": "Got some data!", "data": "recieved"})

    # except Exception as e:
        
    #     print(e)
    #     return Response(status=400,data={"message": "Something went wrong!", "error": True})
        
# @api_view(['GET',  'POST'])
def password_reset(request, *args, **kwargs):

    if request.method == 'GET':

        return render(request, 'reset_password.html')

    else:

        try:

            token = kwargs.get("token", None)
            password = request.data.get("password", None)
            confirm_password = request.data.get("password-confirm", None)

            if (not (token and password and confirm_password)):
                return Response(status=400)
            
            signer = Signer()

            data = signer.unsign_object(token)

            user_id = data["user_id"]

            if(password != confirm_password):

                messages.error(request, "Passwords do not match.")

            else:

                target_user = CustomUser.objects.get(pk=user_id)

                target_user.set_password(password)

                target_user.save()

                messages.success(request, "Password updated! Login to continue...")


            return render(request, 'reset_password.html')

        except Exception as e:

            return Response(status=400)

# @api_view([ 'GET', 'POST' ])
def edit_assignees(request, *args, **kwargs):

    # if(request.method == 'GET'):      

    site_id = kwargs.get("site_id")

    try:

        site = Site.objects.filter(pk=site_id)

        # assert site.exists() 
        # and site.first().assignees.filter(pk=request.user.pk).exists()

        site = site.first()

    except Exception as e:

        print("Error retrieving site: ", e)

        messages.error(request, "Provided site does not exists or not in your access scope.")

        return render(request, "message_display.html")

    if request.method == "POST":

        # time to update
        assignee_id = request.data.get("assignee_id")
        action_type = request.data.get("action_type")

        target_user = CustomUser.objects.get(pk=int(assignee_id))

        if(action_type == "add"):

            site.assignees.add(target_user)
            site._notify = True
            site._assignee_email = target_user.email
        else:

            site.assignees.remove(target_user)
    
        site.save()

        messages.success(request, f"{target_user.email} is added to site successfully!")


    search_query = request.GET.get("search_query", False)

    context = {"site": site}

    already_assignees = site.assignees.all()
    context["already_assignees"] = already_assignees

    if(search_query):

        filtered_users = CustomUser.objects.filter(email__contains=search_query).exclude(id__in=[a.pk for a in list(already_assignees)])
        context["filtered_users"] = filtered_users


    return render(request, "edit_assignees.html", context=context)

# SECTIONS = { 'application_details': "Application Details", 'documents': "Documents" }
SECTIONS = {
    'application_details': "Application Details",
    'documents': "Documents",
    'property_details': "Property Details",
    'site_details': "Site Details",
    'ndma_parameters': "NDMA Parameters",
    'no_approved_plan_details': "NO Approved Plan Details",
    'building_details': "Building Details",
    'technical_details': "Technical Details",
    'valuation_details': "Valuation Details",
    'valuation_extra_items': "Valuation Extra Items",
    'valuation_amenities': "Valuation Amenities",
    'valuation_miscellaneous': "Valuation Miscellaneous",
    'valuation_services': "Valuation Services",
    'property_photographs': "Property Photographs",
    'invoice_details': "Invoice Details",
    'assumptions_remarks': "Assumptions / Remarks",
    'marketability': "Marketability",
    'unit_details': "Unit Details"
}

@login_required
def view_site(request, *args, **kwargs):

    context = {}

    # context = {
    #     'application_details': {
    #         "id": 1,
    #         "fields": [
    #             {
    #                 "name": "purpose_of_report", # from FieldManager instance
    #                 "label": "Purpose of report", # from FieldManager instance
    #                 "value": "", # from XYZ section instance
    #                 "access_level": "NA" # from FieldManager instance
    #             }
    #         ]
    #     }
    # }

    site_id = kwargs.get("site_id")

    target_site = Site.objects.get(pk=site_id)

    report_format = ReportFormat.objects.get(format_name=target_site.application_details.report_format)

    section_obj_memcache = {}

    for section, section_display in SECTIONS.items():
        context[section] = {
            "id": getattr(target_site, section).pk,
            "display_name": section_display,
            'fields': []
        }
        section_obj_memcache[section] = getattr(target_site, section)

    for field in list(report_format.supported_fields.all()):
        if(field.get_access_level(request.user).lower() != "na"):
            context[field.section_name]["fields"].append({
                        "name": field.field_name, # from FieldManager instance
                        "label": field.display_name, # from FieldManager instance
                        "value": getattr(section_obj_memcache[field.section_name], field.field_name), # from XYZ section instance
                        "field_type": field.field_type,
                        "default_value": field.default_value,
                        "choices": getattr(getattr(getattr(getattr(section_obj_memcache[field.section_name],"__class__"), field.field_name), "field"), "choices") if field.field_type == "radio" or field.field_type == "dropdown" or field.field_type == "multiselect-checkbox"  else [],
                        "access_level": field.get_access_level(request.user), # from FieldManager instance
                        "all": getattr(section_obj_memcache[field.section_name], field.field_name).all() if field.field_type == "multiple-image-upload" else [],
                        "model": section_obj_memcache[field.section_name]
                    })
    print(context["valuation_details"])
    return render(request, "view_site.html", context={"context": context})