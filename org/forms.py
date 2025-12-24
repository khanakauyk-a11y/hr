from __future__ import annotations

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Employee


class EmployeeIdAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Employee ID")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class EmployeeCreateForm(forms.Form):
    employee_id = forms.CharField(label="Employee ID", max_length=150)
    full_name = forms.CharField(max_length=150)
    role = forms.ChoiceField(choices=Employee.Role.choices)
    reporting_manager = forms.ModelChoiceField(queryset=Employee.objects.none(), required=False)
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reporting_manager"].queryset = Employee.objects.select_related("user").order_by("user__username")
        self.fields["reporting_manager"].empty_label = "(No manager / top-level)"

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"].strip()
        if User.objects.filter(username=employee_id).exists():
            raise forms.ValidationError("Employee ID already exists.")
        return employee_id

    @transaction.atomic
    def save(self) -> Employee:
        employee_id = self.cleaned_data["employee_id"]
        default_password = getattr(settings, "HR_DEFAULT_PASSWORD", "Welcome@123")

        user = User.objects.create_user(username=employee_id, password=default_password)
        employee = Employee.objects.create(
            user=user,
            full_name=self.cleaned_data["full_name"],
            role=self.cleaned_data["role"],
            reporting_manager=self.cleaned_data.get("reporting_manager"),
            must_change_password=True,
            is_active=bool(self.cleaned_data.get("is_active")),
        )
        return employee


class EmployeeUpdateForm(forms.ModelForm):
    employee_id = forms.CharField(label="Employee ID", max_length=150)

    class Meta:
        model = Employee
        fields = ["employee_id", "full_name", "role", "reporting_manager", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields["employee_id"].initial = self.instance.user.username

        if "reporting_manager" in self.fields:
            self.fields["reporting_manager"].queryset = Employee.objects.select_related("user").order_by(
                "user__username"
            )

        # Consistent Bootstrap styling
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"].strip()
        qs = User.objects.filter(username=employee_id)
        if self.instance and self.instance.user_id:
            qs = qs.exclude(id=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError("Employee ID already exists.")
        return employee_id

    @transaction.atomic
    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.user.username = self.cleaned_data["employee_id"]
        if commit:
            employee.user.save()
            employee.save()
        return employee


