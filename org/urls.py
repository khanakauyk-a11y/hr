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
    
    # Offer Letter
    path("offer-letter/generate/", views.generate_offer_letter, name="generate_offer_letter"),
]


