from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "full_name", "role", "reporting_manager", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "full_name")
