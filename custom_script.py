# from credentials_fetcher import get_social_access_token, get_social_user_data, refresh_social_access_token
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "valuation_site.settings")
import django
# from django.db import models
django.setup()
from core.models import FieldManager, Site, ApplicationDetails, Documents, CustomUser, ReportFormat, PropertyDetails, SiteDetails, NDMAParameters, NOApprovedPlanDetails, BuildingDetails, TechnicalDetails, ValuationAmenities, ValuationDetails, ValuationExtraItems, ValuationMiscellaneous, ValuationServices, PropertyPhotographs, InvoiceDetails, AssumptionsRemarks, UnitDetails, Marketability


# FieldManager.objects.create(field_name="postal_address", display_name="Postal Address", field_type="textbox", coordinator_access_level="edit", technical_engineer_access_level="edit", valuation_engineer_access_level="edit", principal_engineer_access_level="edit")
# print(FieldManager.objects.get(field_name="purpose_of_report").section_name)
# d.formats.add(ReportFormat.objects.get(format_name="Land & Building"))
# d.formats.add(ReportFormat.objects.get(format_name="Composite Method"))
# d.formats.add(ReportFormat.objects.get(format_name="Land & Building 2"))
# d.formats.add(ReportFormat.objects.get(format_name="Composite Method 2"))
# d.save()

import json

# Load JSON data from the file
with open("formated_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

SITE_RELATED_NAMES = {
    "Application Details": "application_details",
    "Documents": "documents",
    "Property Location": "property_details",
    "Site Details": "site_details",
    "NDMA Parameters": "ndma_parameters",
    "NOApproved Plan Details": "no_approved_plan_details",
    "Building Details": "building_details",
    "Technical Details": "technical_details",
    "Valuation Details": "valuation_details",
    "Valuation Details - Extra Items": "valuation_extra_items",
    "Valuation Details - Amenities": "valuation_amenities",
    "Valuation Details - Miscellaneous": "valuation_miscellaneous",
    "Valuation Details - Services": "valuation_services",
    "Property Photographs": "property_photographs",
    "Invoice Details": "invoice_details",
    "Assumptions/Remarks": "assumptions_remarks",
    "Marketability": "marketability",
    "Unit Details": "unit_details"
}
a = {
    "application_details": [
        "purpose_of_report", "bank_name", "property_type", "report_format", "visit_required",
        "branch_name", "bank_contact_person_name", "bank_contact_person_number", "file_no",
        "name_field_title", "name_of_applicant", "loan_type", "property_owner_legal_name",
        "person_met_at_site", "owner_proposed_seller", "site_contact_person_name",
        "site_contact_person_number", "developer_name", "joint_ownership_details",
        "date_of_visit", "date_of_valuation", "due_date_for_visit", "purpose_of_valuation",
        "property_description"
    ],
    "documents": [
        "layout_plan_approving_authority", "layout_plan_approval_no", "layout_plan_document_copy",
        "layout_plan_page_no", "building_plan_approving_authority", "building_plan_approval_no",
        "building_plan_document_copy", "building_plan_page_no", "construction_permission_approving_authority",
        "construction_permission_approval_no", "construction_permission_document_copy",
        "construction_permission_page_no", "bu_permission_approving_authority", "bu_permission_approval_no",
        "bu_permission_document_copy", "bu_permission_page_no", "legal_documents_approving_authority",
        "legal_documents_approval_no", "legal_documents_document_copy", "legal_documents_page_no",
        "date_of_issue_validity", "approved_map_issuing_authority", "genuineness_verified",
        "covered_under_govt_enactments", "agricultural_land_conversion", "valuer_comments_on_authenticity"
    ],
    "property_details": [
        "postal_address", "legal_address", "plot_no", "unit_no", "tps_village", "city_town",
        "ward_taluka", "mandal_district", "property_pin_code", "latitude", "longitude",
        "locality_name", "distance_from_city_centre", "landmark_nearby", "address_of_property",
        "property_state", "property_city", "address_matching", "jurisdiction_municipal_body"
    ],
    "site_details": [
        "boundaries", "boundaries_extended", "property_identified", "matching_boundaries",
        "plot_demarcated", "property_occupied_by", "occupancy_status", "monthly_rent",
        "years_of_occupancy", "tenant_owner_relationship", "floor_no", "property_holding_type",
        "lease_details", "marketability", "type_of_area", "property_class", "locality_class",
        "approach_road_size", "visited_with_representative", "classification_of_locality",
        "development_of_surrounding", "flooding_possibility", "civic_amenities_feasibility",
        "land_topography", "land_shape", "land_use_type", "usage_restriction", "town_planning_approval",
        "plot_type", "road_type", "road_width", "land_locked", "water_potentiality", "underground_sewage",
        "power_supply", "site_advantages", "special_remarks"
    ],
    "ndma_parameters": [
        "nature_of_building", "projected_parts_available", "roof_type", "concrete_grade",
        "sesmic_zone", "soil_slope_vulnerable", "fire_exit", "plan_aspect_ratio",
        "type_of_masonry", "steel_grade", "environment_exposure_condition", "soil_liquefiable",
        "flood_prone_area", "structure_type", "expansion_joints_available", "mortar_type",
        "footing_type", "coastal_regulatory_zone", "ground_slope_above_20"
    ],
    "no_approved_plan_details": [
        "sanctioned_plan_provided", "layout_plan_details", "construction_plan_details",
        "date_of_sanction", "plan_validity", "approving_authority", "approved_usages",
        "number_of_floors"
    ],
    "building_details": [
        "type_of_building", "type_of_construction", "stage_of_construction",
        "extent_of_completion", "nature_and_extent_of_violations", "year_of_construction",
        "age_of_building", "residual_age_of_building", "number_of_floors_and_height",
        "number_of_rooms_living_dining", "number_of_rooms_bedrooms", "number_of_rooms_toilets",
        "number_of_rooms_kitchen", "plinth_area_floor_wise", "condition_exterior",
        "condition_interior", "foundation", "basement", "superstructure", "joinery_doors_windows",
        "rcc_work", "plastering", "flooring_skirting_dadoing", "special_finish",
        "roofing_weatherproof_course", "drainage", "building_compound_wall", "type_of_wiring",
        "class_of_fittings", "number_of_light_points", "fan_points", "spare_plug_points",
        "electrical_installation", "number_of_water_closets", "number_of_wash_basins",
        "number_of_urinals", "water_meter_taps", "plumbing_installation", "roof_height",
        "particular_of_item", "nature_of_apartment", "street_or_road", "locality_description",
        "building_number_of_floors", "type_of_structure", "number_of_dwelling_units",
        "quality_of_construction", "appearance_of_building", "maintenance_of_building",
        "facilities_available", "floor_of_unit"
    ],
    "assumptions_remarks": [
        "qualifications_tir_mitigation", "property_sarfaesi_compliant",
        "belongs_to_social_infrastructure", "land_mortgaged_status",
        "last_two_transactions", "relevant_aspects_on_value"
    ],
    "marketability": [
        "marketability_status"
    ],
    "unit_details": [
        "roof", "flooring", "doors", "windows", "fittings", "finishing",
        "house_tax", "assessment_no", "tax_paid_in_name", "tax_amount",
        "electricity_service_no", "meter_card_maintenance", "maintenance_of_unit",
        "undivided_area", "floor_space_index", "posh_classification", "usage_purpose"
    ],
    "technical_details": [
        "construction_quality", "current_occupant", "lift_available", "number_of_lifts",
        "separate_independent_access", "floor_wise_occupancy"
    ],
    "valuation_details": [
        "land_area_documents", "land_area_plan", "land_area_site_visit", "land_square_meter",
        "land_square_yard", "land_square_feet", "super_land_square_meter",
        "super_land_square_yard", "super_land_square_feet", "carpet_area_square_meter",
        "carpet_area_square_yard", "carpet_area_square_feet", "built_up_area_square_meter",
        "built_up_area_square_yard", "built_up_area_square_feet", "super_built_up_area_square_meter",
        "super_built_up_area_square_yard", "super_built_up_area_square_feet",
        "guideline_land_rate_provided_for", "guideline_rate_land_square_meter",
        "market_land_rate_provided_for", "market_rate_land_square_meter",
        "market_rate_land_square_yard", "market_rate_land_square_feet",
        "guideline_construction_rate_square_meter", "guideline_rate_provided_for",
        "guideline_rate_square_meter", "market_construction_rate_provided_for",
        "construction_rate_square_meter", "construction_rate_square_yard",
        "construction_rate_square_feet", "composite_rate_provided_for",
        "composite_rate_square_meter", "composite_rate_square_yard",
        "composite_rate_square_feet", "realizable_value_percentage",
        "distress_value_percentage", "depreciation_value_percentage",
        "combined_additional_value", "book_value"
    ],
    "valuation_extra_items": [
        "portico", "ornamental_front_door", "sit_out_verandah", "overhead_water_tank",
        "extra_steel_gates", "combined_value_extra_items"
    ],
    "valuation_amenities": [
        "wardrobes", "glazed_tiles", "extra_sinks_bath_tub", "marble_ceramic_flooring",
        "interior_decorations", "architectural_elevation", "panelling_works",
        "aluminium_works", "aluminium_hand_rails", "false_ceiling", "combined_value_amenities"
    ],
    "valuation_miscellaneous": [
        "separate_toilet_room", "separate_lumber_room", "separate_water_tank_sump",
        "trees_gardening", "combined_value_miscellaneous"
    ],
    "valuation_services": [
        "water_supply_arrangements", "compound_wall", "cb_deposits_fittings",
        "pavement", "combined_value_services"
    ],
    "property_photographs": [
        "property_front_view", "google_earth_photograph", "property_photographs"
    ],
    "invoice_details": [
        "date_of_invoice", "charges_amount", "other_expenses", "gst_included",
        "cgst", "sgst", "total_invoice_amount", "payment_mode"
    ]
}
'''
SITE_RELATED_NAMES = {
    "Application Details": "application_details",
    "Documents": "documents",
    "Property Location": "property_details",
    "Site Details": "site_details",
    "NDMA Parameters": "ndma_parameters",
    "NOApproved Plan Details": "no_approved_plan_details",
    "Building Details": "building_details",
    "Technical Details": "technical_details",
    "Valuation Details": "valuation_details",
    "Valuation Details - Extra Items": "valuation_extra_items",
    "Valuation Details - Amenities": "valuation_amenities",
    "Valuation Details - Miscellaneous": "valuation_miscellaneous",
    "Valuation Details - Services": "valuation_services",
    "Property Photographs": "property_photographs",
    "Invoice Details": "invoice_details",
    "Assumptions/Remarks": "assumptions_remarks",
    "Marketability": "marketability",
    "Unit Details": "unit_details"
}
[
  {
    "Section Title": "Application Details",
    "Field Name": "Purpose of Report",
    "Field Type": "Dropdown",
    "Field Options": "Private Purpose, For Bank, Visa Purpose, Education Loan",
    "Default Value": "",
    "Co-Ordinator": "Edit",
    "Technical Engineer": "View",
    "Valuation Engineer": "Edit",
    "Principal Engineer": "Edit",
    "Land & Building": "TRUE",
    "Composite Method": "TRUE",
    "Land & Building 2.0": "TRUE",
    "Composite Method 2.0": "TRUE"
  },

  
# FieldManager.objects.create(field_name="postal_address", display_name="Postal Address", field_type="textbox", coordinator_access_level="edit", technical_engineer_access_level="edit", valuation_engineer_access_level="edit", principal_engineer_access_level="edit")
# d.formats.add(ReportFormat.objects.get(format_name="Land & Building"))
# d.formats.add(ReportFormat.objects.get(format_name="Composite Method"))
# d.formats.add(ReportFormat.objects.get(format_name="Land & Building 2"))
# d.formats.add(ReportFormat.objects.get(format_name="Composite Method 2"))
"Valuation Details - Extra Items": "valuation_extra_items",
    "Valuation Details - Amenities": "valuation_amenities",
    "Valuation Details - Miscellaneous": "valuation_miscellaneous",
    "Valuation Details - Services": "valuation_services",
    "Property Photographs": "property_photographs",
    "Invoice Details": "invoice_details",
'''
# for row in data:
#     try:
#         row["Section Title"] = SITE_RELATED_NAMES[row["Section Title"]]
#         # for section_field in a[row["Section Title"]]:
#         #     FieldManager.objects.create(field_name=section_field)

#     except Exception as e:
#         print("Failed For: ",row["Section Title"])
#         print(e)
#         break

# selected_sections = list(a.keys())
# finalized_entries = []
# finalized_field_names = []
# for section in selected_sections:
#     for row in data:
#         if row["Section Title"] == section:
#             finalized_entries.append(row)
#     finalized_field_names.extend(a[section])

# print(f"Entires :", len(finalized_entries), " Field Names: ", len(finalized_field_names))
# # print(FieldManager.objects.count())
# for i in range(len(finalized_entries)):
#     try:
#         entry_i = finalized_entries[i]
#         d = FieldManager.objects.create(field_name=finalized_field_names[i], section_name=entry_i["Section Title"], display_name=entry_i["Field Name"], field_type=entry_i["Field Type"], coordinator_access_level=entry_i["Co-Ordinator"].lower(), technical_engineer_access_level=entry_i["Technical Engineer"].lower(), valuation_engineer_access_level=entry_i["Valuation Engineer"].lower(), principal_engineer_access_level=entry_i["Principal Engineer"].lower())
#         if(entry_i["Land & Building"] == "TRUE"):
#             d.formats.add(ReportFormat.objects.get(format_name="Land & Building"))
#         if(entry_i["Composite Method"] == "TRUE"):
#             d.formats.add(ReportFormat.objects.get(format_name="Composite Method"))
#         if(entry_i["Land & Building 2.0"] == "TRUE"):
#             d.formats.add(ReportFormat.objects.get(format_name="Land & Building 2.0"))
#         if(entry_i["Composite Method 2.0"] == "TRUE"):
#             d.formats.add(ReportFormat.objects.get(format_name="Composite Method 2.0"))

#         d.save()

#     except Exception as e:
#         print(finalized_field_names[i])
#         print(e)

# mapper = {
#     "Textbox": "textbox",
#     "Radio Button": "radio",
#     "Multiselect Checkbox": "multiselect-checkbox",
#     "Textbox - Number": "textbox-number",
#     "Textbox - percentage": "textbox-percentage",
#     "": "blank",
#     "File Upload": "file-upload",
#     "Multiple Image Upload": "multiple-image-upload",
#     "Date Picker": "date",
#     "Auto Calculate": "auto-calculate",
#     "Dropdown": "dropdown"
# }

# for j in mapper.keys():

#     grp = FieldManager.objects.filter(field_type=j)

#     for elem in list(grp):

#         elem.field_type = mapper[j]
#         elem.save()    

site = Site.objects.first()
# property_details = PropertyDetails.objects.create(
#     site=site,
#     postal_address="123 Main Street, Jodhpur",
#     legal_address="Block A, Plot 80, Jodhpur",
#     plot_no="F.P. No. 80, Old Survey No. 47 (Survey No. 141)",
#     unit_no="A-101",
#     tps_village="T.P.S. No. 4 / Jodhpur",
#     city_town="Jodhpur",
#     ward_taluka="Sardarpura",
#     mandal_district="Jodhpur",
#     property_pin_code="342001",
#     latitude="26.2389° N",
#     longitude="73.0243° E",
#     locality_name="Shastri Nagar",
#     distance_from_city_centre="5 km",
#     landmark_nearby="Umaid Bhawan Palace",
#     address_of_property="123 Main Street, Shastri Nagar, Jodhpur",
#     property_state="Rajasthan",
#     property_city="Jodhpur",
#     address_matching="Yes",
#     jurisdiction_municipal_body="Jodhpur Municipal Corporation"
# )

# # SiteDetails
# site_details = SiteDetails.objects.create(
#     site=site,
#     boundaries="North: Road, South: Plot 81, East: Plot 79, West: Road",
#     boundaries_extended="North: 30ft Road, South: Plot 81 owned by Mr. Sharma, East: Plot 79 owned by Mrs. Verma, West: 20ft Road",
#     property_identified="Yes",
#     matching_boundaries="Yes",
#     plot_demarcated="Yes",
#     property_occupied_by="Self",
#     occupancy_status="SORP",
#     monthly_rent="NA",
#     years_of_occupancy="NA",
#     tenant_owner_relationship="NA",
#     floor_no="Ground Floor",
#     property_holding_type="Freehold",
#     lease_details="NA",
#     marketability="Good",
#     type_of_area="Residential Area",
#     property_class="High",
#     locality_class="Urban",
#     approach_road_size=">15 ft",
#     visited_with_representative="No",
#     classification_of_locality="Upper Middle Class",
#     development_of_surrounding="Good",
#     flooding_possibility="No",
#     civic_amenities_feasibility="Nearby",
#     land_topography="Flat land with no undulations",
#     land_shape="Regular Rectangle",
#     land_use_type="Residential",
#     usage_restriction="NA",
#     town_planning_approval="Yes",
#     plot_type="Corner Plot",
#     road_type="CC Road",
#     road_width="More than 20 ft",
#     land_locked="No",
#     water_potentiality="Yes",
#     underground_sewage="Yes",
#     power_supply="Yes",
#     site_advantages="Regular shape, Marketable size Located at a developed residential area, Near to major roads. Located within a compounded residential society with common amenities & facilities etc.",
#     special_remarks="NA"
# )

# # NDMAParameters
# ndma_parameters = NDMAParameters.objects.create(
#     site=site,
#     nature_of_building="Residential",
#     projected_parts_available="No",
#     roof_type="RCC",
#     concrete_grade="M25",
#     sesmic_zone="Zone III",
#     soil_slope_vulnerable="No",
#     fire_exit="Yes",
#     plan_aspect_ratio="Yes",
#     type_of_masonry="Brick Masonry",
#     steel_grade="Fe 500",
#     environment_exposure_condition="Moderate",
#     soil_liquefiable="No",
#     flood_prone_area="No",
#     structure_type="RCC",
#     expansion_joints_available="Yes",
#     mortar_type="Cement Mortar 1:4",
#     footing_type="Isolated Footing",
#     coastal_regulatory_zone="No",
#     ground_slope_above_20="No"
# )

# # NOApprovedPlanDetails
# import datetime
# no_approved_plan_details = NOApprovedPlanDetails.objects.create(
#     site=site,
#     sanctioned_plan_provided="Yes",
#     layout_plan_details="Layout plan No. LYT/2022/456",
#     construction_plan_details="Construction plan No. CP/2022/789",
#     date_of_sanction=datetime.date(2022, 5, 15),
#     plan_validity="5 years",
#     approving_authority="Jodhpur Development Authority",
#     approved_usages="Residential",
#     number_of_floors="2"
# )

# BuildingDetails
# building_details = BuildingDetails.objects.create(
#     site=site,
#     type_of_building="Residential",
#     type_of_construction="RCC Frame Structure",
#     stage_of_construction="Completed",
#     extent_of_completion="NA",
#     nature_and_extent_of_violations="NA",
#     year_of_construction="2020",
#     age_of_building="3",
#     residual_age_of_building="50 Years subjected to proper Maintenance",
#     number_of_floors_and_height="Ground + First + Second floor, Avg 3.2 meter",
#     number_of_rooms_living_dining="1",
#     number_of_rooms_bedrooms="3",
#     number_of_rooms_toilets="3",
#     number_of_rooms_kitchen="1",
#     plinth_area_floor_wise="Ground Floor: 120 sqm, First Floor: 120 sqm, Second Floor: 120 sqm",
#     condition_exterior="Good",
#     condition_interior="Good",
#     foundation="RCC Footing",
#     basement="NA",
#     superstructure="RCC Frame",
#     joinery_doors_windows="Door - Wooden, Windows - Wooden / MS grill, Alu. Section glazed / MS grill",
#     rcc_work="Brick Masonry",
#     plastering="Cement Plaster",
#     flooring_skirting_dadoing="Vitrified",
#     special_finish="NA",
#     roofing_weatherproof_course="NA",
#     drainage="Yes",
#     building_compound_wall="Yes",
#     type_of_wiring="Concealed",
#     class_of_fittings="Superior",
#     number_of_light_points="----",
#     fan_points="----",
#     spare_plug_points="----",
#     electrical_installation="----",
#     number_of_water_closets="----",
#     number_of_wash_basins="----",
#     number_of_urinals="----",
#     water_meter_taps="----",
#     plumbing_installation="----",
#     roof_height="Average 3 mtr",
#     particular_of_item="Average 3 mtr",
#     nature_of_apartment="Residential",
#     street_or_road="30 ft wide CC Road",
#     locality_description="The site benefits from well-developed surrounding areas for both residential and commercial purposes, with easy access to a range of nearby amenities.",
#     building_number_of_floors=3,
#     type_of_structure="RCC Frame Structure",
#     number_of_dwelling_units="As per plan",
#     quality_of_construction="Good",
#     appearance_of_building="Good",
#     maintenance_of_building="Good",
#     facilities_available="Lift,Protected Water Supply,Car Parking",
#     floor_of_unit="Ground Floor"
# )
# print(site.unit_details)
# s = site.application_details
# s.report_format = "Composite Method"
# s.save()
# # UnitDetails
# unit_details = UnitDetails.objects.create(
#     site=site,
#     roof="RCC Slab",
#     flooring="Vitrified,Kota",
#     doors="Wooden,MS Gate",
#     windows="Aluminium section glazed,Glass Window",
#     fittings="Open",
#     finishing="Cement plaster with wall putty",
#     house_tax="NA",
#     assessment_no="NA",
#     tax_paid_in_name="NA",
#     tax_amount="NA",
#     electricity_service_no="NA",
#     meter_card_maintenance="NA",
#     maintenance_of_unit="Good",
#     undivided_area="120 sq.m.",
#     floor_space_index="1.8",
#     posh_classification="I class",
#     usage_purpose="Residential"
# )
# UnitDetails.objects.all().delete()
# BuildingDetails.objects.all().delete()
# # Marketability
# marketability = Marketability.objects.create(
#     site=site,
#     marketability_status="Good, as the developed area with excellent connectivity and amenities"
# )

# # AssumptionsRemarks
# assumptions_remarks = AssumptionsRemarks.objects.create(
#     site=site,
#     qualifications_tir_mitigation="NA",
#     property_sarfaesi_compliant="Yes",
#     belongs_to_social_infrastructure="No",
#     land_mortgaged_status="NA",
#     last_two_transactions="No transactions in last 3 years",
#     relevant_aspects_on_value="Property values in the area have increased by 15% in the past year"
# )

# # TechnicalDetails
# technical_details = TechnicalDetails.objects.create(
#     site=site,
#     construction_quality="Good",
#     current_occupant="Owner",
#     lift_available="No",
#     number_of_lifts="0",
#     separate_independent_access="Yes",
#     floor_wise_occupancy="Ground Floor: Owner, First Floor: Owner Family, Second Floor: Vacant"
# )

# # ValuationDetails
# valuation_details = ValuationDetails.objects.create(
#     site=site,
#     land_area_documents="200 sq.m.",
#     land_area_plan="200 sq.m.",
#     land_area_site_visit="200 sq.m.",
#     land_square_meter="200",
#     land_square_yard="239.2",
#     land_square_feet="2152.8",
#     super_land_square_meter="220",
#     super_land_square_yard="263.12",
#     super_land_square_feet="2368.1",
#     carpet_area_square_meter="150",
#     carpet_area_square_yard="179.4",
#     carpet_area_square_feet="1614.6",
#     built_up_area_square_meter="180",
#     built_up_area_square_yard="215.28",
#     built_up_area_square_feet="1937.5",
#     super_built_up_area_square_meter="200",
#     super_built_up_area_square_yard="239.2",
#     super_built_up_area_square_feet="2152.8",
#     guideline_land_rate_provided_for="Land",
#     guideline_rate_land_square_meter="30000",
#     market_land_rate_provided_for="Land",
#     market_rate_land_square_meter="35000",
#     market_rate_land_square_yard="29288",
#     market_rate_land_square_feet="3254",
#     guideline_construction_rate_square_meter="14500",
#     guideline_rate_provided_for="Built Up",
#     guideline_rate_square_meter="45000",
#     market_construction_rate_provided_for="Built Up",
#     construction_rate_square_meter="50000",
#     construction_rate_square_yard="41840",
#     construction_rate_square_feet="4649",
#     composite_rate_provided_for="Built Up",
#     composite_rate_square_meter="85000",
#     composite_rate_square_yard="71128",
#     composite_rate_square_feet="7897",
#     realizable_value_percentage="90",
#     distress_value_percentage="75",
#     depreciation_value_percentage="0",
#     combined_additional_value="150000",
#     book_value="17000000"
# )

# # ValuationExtraItems
# valuation_extra_items = ValuationExtraItems.objects.create(
#     site=site,
#     portico="50000",
#     ornamental_front_door="15000",
#     sit_out_verandah="30000",
#     overhead_water_tank="25000",
#     extra_steel_gates="20000",
#     combined_value_extra_items="140000"
# )

# # ValuationAmenities
# valuation_amenities = ValuationAmenities.objects.create(
#     site=site,
#     wardrobes="75000",
#     glazed_tiles="50000",
#     extra_sinks_bath_tub="35000",
#     marble_ceramic_flooring="120000",
#     interior_decorations="80000",
#     architectural_elevation="40000",
#     panelling_works="25000",
#     aluminium_works="30000",
#     aluminium_hand_rails="15000",
#     false_ceiling="55000",
#     combined_value_amenities="525000"
# )

# # ValuationMiscellaneous
# valuation_miscellaneous = ValuationMiscellaneous.objects.create(
#     site=site,
#     separate_toilet_room="25000",
#     separate_lumber_room="20000",
#     separate_water_tank_sump="30000",
#     trees_gardening="15000",
#     combined_value_miscellaneous="90000"
# )

# # ValuationServices
# valuation_services = ValuationServices.objects.create(
#     site=site,
#     water_supply_arrangements="40000",
#     compound_wall="80000",
#     cb_deposits_fittings="25000",
#     pavement="35000",
#     combined_value_services="180000"
# )
# import datetime
# invoice_details = InvoiceDetails.objects.create(
#     site=site,
#     date_of_invoice=datetime.date(2023, 6, 15),
#     charges_amount="15000",
#     other_expenses="2000",
#     gst_included="Yes",
#     cgst="1530",
#     sgst="1530",
#     total_invoice_amount="20060",
#     payment_mode="Bank Transfer"
# )
# PropertyPhotographs.objects.create(site=site)