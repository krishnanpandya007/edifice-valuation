from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import CustomUser, Site, Document, Comment, ReportFormat, ImageAttachment, ApplicationDetails, Documents, PropertyDetails, SiteDetails, NDMAParameters, NOApprovedPlanDetails, BuildingDetails, UnitDetails, Marketability, AssumptionsRemarks, TechnicalDetails, ValuationDetails, ValuationExtraItems, ValuationAmenities, ValuationMiscellaneous, ValuationServices, PropertyPhotographs, InvoiceDetails
from datetime import datetime
from django.core.signing import Signer
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
import traceback 
import pdfkit
from django.http import HttpResponse
import os
from jinja2 import Environment, FileSystemLoader

# For DOCX
from spire.doc import Document
from spire.doc import FileFormat, XHTMLValidationType

ReportStatus = Site.ReportStatus
Roles = CustomUser.Roles

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
            ap = [s.application_details for s in list(sites)]
            # print(ap[0].bank_name)    
            ap = [ad for ad in ap if s in ad.bank_name.lower()]
            sites = sites.filter(pk__in=[a.site.pk for a in ap])

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

        return render(request, 'home.html', context={"sites": page_obj, "create_site_helpers": {"report_formats": ApplicationDetails.report_format.field.choices} })

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
        assignee_id = request.POST.get("assignee_id")
        action_type = request.POST.get("action_type")

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
report_status_actions = {
    ReportStatus.REPORT_REQUEST_SUBMITTED: {
        "next": [ReportStatus.VISIT_ASSIGNED],
        "access_roles": [Roles.COORDINATOR]
    },
    ReportStatus.VISIT_ASSIGNED: {
        "next": [ReportStatus.VISIT_COMPLETED],
        "access_roles": [Roles.TECHNICAL_ENGINEER]
    },
    ReportStatus.VISIT_COMPLETED: {
        "next": [ReportStatus.VISIT_APPROVED, ReportStatus.VISIT_REASSIGNED],
        "access_roles": [Roles.VALUATION_ENGINEER]
    },
    ReportStatus.VISIT_APPROVED: {
        "next": [ReportStatus.REPORT_IN_PROGRESS],
        "access_roles": [Roles.VALUATION_ENGINEER]
    },
    ReportStatus.VISIT_REASSIGNED: {
        "next": [ReportStatus.VISIT_REASSIGNED, ReportStatus.VISIT_APPROVED],
        "access_roles": [Roles.VALUATION_ENGINEER]
    },
    ReportStatus.REPORT_GENERATED: {
        "next": [ReportStatus.REPORT_COMPLETED, ReportStatus.REPORT_REASSIGNED],
        "access_roles": [Roles.PRINCIPLE_ENGINEER]
    },
    ReportStatus.REPORT_IN_PROGRESS: {
        "next": [ReportStatus.REPORT_GENERATED],
        "access_roles": [Roles.VALUATION_ENGINEER]
    },
    ReportStatus.REPORT_COMPLETED: {
        "next": [ReportStatus.REPORT_SUBMITTED],
        "access_roles": [Roles.PRINCIPLE_ENGINEER, Roles.COORDINATOR]
    },
    ReportStatus.REPORT_SUBMITTED: {
        "next": [ReportStatus.REPORT_APPROVED],
        "access_roles": [Roles.PRINCIPLE_ENGINEER]
    },
    ReportStatus.REPORT_APPROVED: {
        "next": [ReportStatus.COMPLETE],
        "access_roles": [Roles.PRINCIPLE_ENGINEER, Roles.COORDINATOR]
    },
    ReportStatus.COMPLETE: {
        "next": [],
        "access_roles": []
    },
    ReportStatus.REPORT_REASSIGNED: {
        "next": [ReportStatus.REPORT_IN_PROGRESS],
        "access_roles": [Roles.VALUATION_ENGINEER]
    }
}

@login_required
def view_site(request, *args, **kwargs):

    try:

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

        if (request.method == "POST"):

            data = {**request.POST, **request.FILES}
            print(data)
            for k, v in data.items():
                data[k] = v[0]

            section_name = data.get('section-name')

            assert section_name in SECTIONS.keys(), "Invalid section name"

            target_section = getattr(target_site, section_name)

            field_managers = report_format.supported_fields.filter(field_name__in=data.keys())

            # datetime.strptime('-'.join(data.get(field_manager.field_name).split('/')[::-1]), "%Y-%d-%m").date()

            for field_manager in list(field_managers):

                if(field_manager.get_access_level(request.user).lower() == "edit"):

                    # remaining field types [auto-calculate, file-upload, image-upload, multiple-image-upload, blank]

                    if field_manager.field_type in ["textbox-percentage", "dropdown", "radio", "textbox", "textbox-number"]:
                        print(field_manager.field_name)
                        setattr(target_section, field_manager.field_name, data.get(field_manager.field_name))

                    elif field_manager.field_type == "date":

                        setattr(target_section, field_manager.field_name, datetime.strptime('-'.join(data.get(field_manager.field_name).split('/')[::-1]), "%Y-%d-%m").date())

                    elif field_manager.field_type == "multiselect-checkbox":

                        print(target_section)
                        print(field_manager.field_name)
                        setattr(target_section, field_manager.field_name, ','.join(data.getlist(field_manager.field_name)))

                    elif field_manager.field_type == "file-upload" or field_manager.field_type == "image-upload":

                        file_action = data.get(f"__include__@{field_manager.field_name}")

                        if(file_action == "add"):

                            setattr(target_section, field_manager.field_name, data.get(field_manager.field_name))

                        elif (file_action == "remove"):

                            setattr(target_section, field_manager.field_name, None)

                        else:
                            # file_action==constant

                            pass
                        
                        
                    elif field_manager.field_type == "multiple-image-upload":

                        # remove files
                        # add files

                        attachment_pool = getattr(target_section, field_manager.field_name).all()
                        remove_list = data.get(f"{field_manager.field_name}-remove-list")

                        if (remove_list):
                            remove_file_pks = [ int(pk) for pk in remove_list.split(",")]

                            if (len(remove_file_pks) > 0):

                                delete_pool = attachment_pool.filter(pk__in=remove_file_pks)
                                delete_pool.delete()

                        add_tmp_ids_pool = [ f.split("@")[2] for f in data.keys() if f.startswith(f"{field_manager.field_name}@name@")]

                        for tmp_id in add_tmp_ids_pool:

                            file = data.get(f"{field_manager.field_name}@file@{tmp_id}")
                            name = data.get(f"{field_manager.field_name}@name@{tmp_id}")

                            if (file and name):

                                img = ImageAttachment.objects.create(name=name, attachment=file)

                                getattr(target_section, field_manager.field_name).add(img)




            target_section.save()


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
                            "filename": getattr(section_obj_memcache[field.section_name], field.field_name).name.split("/")[-1] if field.field_type == "file-upload" or field.field_type == "image-upload" else "",
                            "model": section_obj_memcache[field.section_name]
                        })

        return render(request, "view_site.html", context={"context": context, "site_id": site_id, "report_status": target_site.report_status.replace('_', ' ').capitalize(), "next_report_statuses": report_status_actions[target_site.report_status]})

    except AssertionError as ae:

        messages.error(request, str(ae))

        return render(request, 'message_display.html')


    except Exception as e:
        print(e)
        print(traceback.format_exc())
        messages.error(request, f"Something went wrong!")

        return render(request, 'message_display.html')

@login_required
def create_site(request):

    try:

        assert request.user.role == "COORDINATOR", "Only Coordinator can create site."
        report_format = request.POST.get('report_format')
        branch_name = request.POST.get('branch_name')
        print(report_format, branch_name)
        print(request.POST)
        # print(request.data)

        assert report_format and branch_name, "Please provide all necessary details to create site."

        new_site = Site.objects.create(creator=request.user)

        ApplicationDetails.objects.create(site=new_site, report_format=report_format, branch_name=branch_name)
        Documents.objects.create(site=new_site)
        PropertyDetails.objects.create(site=new_site)
        SiteDetails.objects.create(site=new_site)
        NDMAParameters.objects.create(site=new_site)
        NOApprovedPlanDetails.objects.create(site=new_site)
        BuildingDetails.objects.create(site=new_site)
        UnitDetails.objects.create(site=new_site)
        Marketability.objects.create(site=new_site)
        AssumptionsRemarks.objects.create(site=new_site)
        TechnicalDetails.objects.create(site=new_site)
        ValuationDetails.objects.create(site=new_site)
        ValuationExtraItems.objects.create(site=new_site)
        ValuationAmenities.objects.create(site=new_site)
        ValuationMiscellaneous.objects.create(site=new_site)
        ValuationServices.objects.create(site=new_site)
        PropertyPhotographs.objects.create(site=new_site)
        InvoiceDetails.objects.create(site=new_site)

        return redirect('view_site', site_id=new_site.pk)

    except AssertionError as ae:

        messages.error(request, str(ae))

        return render(request, 'message_display.html')


    except Exception as e:
        print(e)
        print(traceback.format_exc())
        messages.error(request, f"Something went wrong!")

        return render(request, 'message_display.html')
    
def export_file(request, format_type, site_id):
    # Step 1: Context data
    # context = {
    #     'username': 'Krishnan',
    #     'date': datetime.date.today().strftime('%Y-%m-%d'),
    #     'items': ['ReachOut', 'Flutter App', 'Analytics']
    # }

    # Step 2: Render HTML with Jinja2
    site = None
    try:
        site = Site.objects.get(pk=int(site_id))
        assert site, "Site does not exist"
    except AssertionError as ae:
        print(ae)
        messages.error(request, str(ae))
        return render(request, 'message_display.html')

    application_details = site.application_details
    
    env = Environment(loader=FileSystemLoader(os.path.join(settings.BASE_DIR)))
    template = env.get_template('composite_2.html')

    rendered_html = template.render(
        site=site,
        image_host="C:\\Users\\krishnan\\valuation_site\\"
    )

    # Step 3: Based on format, generate and return file
    if format_type == 'pdf':
        pdf_data = pdfkit.from_string(rendered_html, False)
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="export.pdf"'
        return response

    elif format_type == 'docx':
        html_path = os.path.join(settings.BASE_DIR, 'composite_2.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        output_path = os.path.join(settings.BASE_DIR, 'HtmlToWord.docx')

        document = Document()
        document.LoadFromFile(html_path, FileFormat.Html, XHTMLValidationType.none)
        document.SaveToFile(output_path, FileFormat.Docx2016)
        document.Close()

        with open(output_path, 'rb') as docx_file:
            response = HttpResponse(docx_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename="export.docx"'
            return response

    else:
        return HttpResponse("Invalid format", status=400)
    
'''
report_status_actions = {
    ReportStatus.REPORT_REQUEST_SUBMITTED: {
        "next": [ReportStatus.VISIT_ASSIGNED],
        "access_roles": [Roles.COORDINATOR]
    },
'''
def change_status(request, site_id):

    try:
        site = Site.objects.get(pk=site_id)

        next_status = request.POST["next_status"]

        if request.user.role in report_status_actions[site.report_status]["access_roles"]:

            site.report_status = next_status
            site.save()
            return redirect('view_site', site_id=site_id)

        else:
            messages.error(request, f"You do not have right to change status!")

            return render(request, 'message_display.html')


    except Exception as e:
        print(e)
        messages.error(request, f"Something went wrong!")

        return render(request, 'message_display.html')
