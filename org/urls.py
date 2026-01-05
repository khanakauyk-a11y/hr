from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("change-password/", views.change_password, name="change_password"),
    path("org/", views.org_chart, name="org_chart"),

    # Admin portal
    path("admin/", views.admin_home, name="admin_home"),
    path("admin/employees/", views.employee_list, name="employee_list"),
    path("admin/employees/new/", views.employee_create, name="employee_create"),
    path("admin/employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("admin/employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("admin/employees/<int:pk>/reset-password/", views.employee_reset_password, name="employee_reset_password"),
    
    # Offer Letter Approval Workflow
    path("offer-letter/generate/", views.generate_offer_letter, name="generate_offer_letter"),
    path("offer-letters/", views.offer_letters_list, name="offer_letters_list"),
    path("offer-letters/approve/", views.hr_approval_dashboard, name="hr_approval_dashboard"),
    path("offer-letters/<int:pk>/approve/", views.approve_offer_letter, name="approve_offer_letter"),
    path("offer-letters/<int:pk>/reject/", views.reject_offer_letter, name="reject_offer_letter"),
    path("offer-letters/<int:pk>/download/", views.download_offer_letter, name="download_offer_letter"),
    # Public candidate download (no login required)
    path("offer/<str:token>/", views.candidate_download_page, name="candidate_download"),
    
    # Daily Reports
    path("report/submit/", views.submit_daily_report, name="submit_daily_report"),
    path("reports/dashboard/", views.manager_reports_dashboard, name="manager_reports_dashboard"),
    path("reports/<int:pk>/", views.view_report_detail, name="view_report_detail"),
]


