from core.models import CustomUser, Site
ReportStatus = Site.ReportStatus
Roles = CustomUser.Roles

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
