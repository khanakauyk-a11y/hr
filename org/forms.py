from __future__ import annotations

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Employee, DailyReport


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
    reporting_manager = forms.ModelChoiceField(queryset=Employee.objects.none(), required=False, label="Parent Manager")
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
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
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        reporting_manager = cleaned_data.get('reporting_manager')
        
        # Validate hiring limits if reporting manager is set
        if reporting_manager and role:
            can_hire, error_msg = reporting_manager.can_hire_role(role)
            if not can_hire:
                raise forms.ValidationError(error_msg)
        
        return cleaned_data

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


class OfferLetterForm(forms.Form):
    """Form for generating offer letters"""
    reference_number = forms.CharField(
        max_length=100,
        initial="EOM/HR/DP/095/25/",
        help_text="e.g., EOM/HR/DP/095/25/711"
    )
    offer_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Offer Letter Date"
    )
    candidate_name = forms.CharField(max_length=150, label="Candidate Full Name")
    candidate_email = forms.EmailField(label="Candidate Email", help_text="Email for sending the offer letter link")
    designation = forms.ChoiceField(choices=Employee.Role.choices, label="Position/Designation")
    department = forms.CharField(max_length=100, label="Department")
    joining_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date of Joining"
    )
    annual_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Annual Salary (in Rupees)",
        help_text="Enter numeric value, e.g., 600000"
    )
    salary_in_words = forms.CharField(
        max_length=200,
        label="Salary in Words",
        help_text="e.g., Six Lakh"
    )
    team_details = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Team Structure Details",
        initial="In this role, you will be responsible for recruiting four direct reportees and facilitating team growth through their leadership.",
        help_text="Optional: Team management responsibilities"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date if not provided
        if 'offer_date' not in self.initial:
            import datetime
            self.initial['offer_date'] = datetime.date.today()
        
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class DailyReportForm(forms.ModelForm):
    """Form for submitting daily work reports"""
    
    class Meta:
        model = DailyReport
        fields = ['tasks_completed', 'challenges', 'next_day_plan', 'joining_date', 'today_hiring', 'total_hiring', 'sales']
        widgets = {
            'tasks_completed': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List the tasks you completed today...'}),
            'challenges': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any blockers or challenges? (Optional)'}),
            'next_day_plan': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What do you plan to work on tomorrow? (Optional)'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select joining date (Optional)'}),
            'today_hiring': forms.NumberInput(attrs={'placeholder': 'Number of people hired today', 'min': '0'}),
            'total_hiring': forms.NumberInput(attrs={'placeholder': 'Total hiring count', 'min': '0'}),
            'sales': forms.NumberInput(attrs={'placeholder': 'Sales amount', 'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
