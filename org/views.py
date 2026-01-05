from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .decorators import admin_required, can_add_employees_required, employee_required
from .forms import EmployeeCreateForm, EmployeeIdAuthenticationForm, EmployeeUpdateForm, OfferLetterForm, DailyReportForm
from .models import Employee, DailyReport
from .offer_letter_pdf import generate_offer_letter_pdf
from django.utils import timezone
from datetime import date, datetime


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


class UserLoginView(LoginView):
    template_name = "login.html"
    authentication_form = EmployeeIdAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        if not hasattr(self.request.user, "employee"):
            logout(self.request)
            messages.error(self.request, "No employee profile found for this account.")
            return redirect("login")
        if not self.request.user.employee.is_active:
            logout(self.request)
            messages.error(self.request, "This account is inactive.")
            return redirect("login")
        if self.request.user.employee.must_change_password:
            return redirect("change_password")
        return response


@require_http_methods(["GET", "POST"])
def user_login(request: HttpRequest) -> HttpResponse:
    view = UserLoginView.as_view(extra_context={"title": "User Login"})
    return view(request)


@require_http_methods(["GET", "POST"])
def admin_login(request: HttpRequest) -> HttpResponse:
    view = UserLoginView.as_view(extra_context={"title": "Admin Login"})
    response = view(request)

    # If login succeeded, enforce admin role
    if request.user.is_authenticated:
        if not hasattr(request.user, "employee") or not request.user.employee.can_access_admin_portal():
            logout(request)
            messages.error(request, "This account is not an admin.")
            return redirect("admin_login")

    return response


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home")


@employee_required
def dashboard(request: HttpRequest) -> HttpResponse:
    employee: Employee = request.user.employee
    if employee.must_change_password:
        return redirect("change_password")
    if employee.can_access_admin_portal():
        return redirect("admin_home")
    return redirect("org_chart")


@employee_required
@require_http_methods(["GET", "POST"])
def change_password(request: HttpRequest) -> HttpResponse:
    employee: Employee = request.user.employee
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        employee.must_change_password = False
        employee.save(update_fields=["must_change_password"])
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated.")
        return redirect("dashboard")
    return render(request, "change_password.html", {"form": form})


def _build_tree(root: Employee, employees: list[Employee]) -> dict[str, Any]:
    by_manager: dict[int | None, list[Employee]] = {}
    for e in employees:
        by_manager.setdefault(e.reporting_manager_id, []).append(e)

    def node_for(emp: Employee) -> dict[str, Any]:
        children = [node_for(c) for c in by_manager.get(emp.id, [])]
        hiring_capacity = emp.get_hiring_capacity()
        return {
            "employee": emp, 
            "children": children,
            "hiring_capacity": hiring_capacity,
        }

    return node_for(root)


@employee_required
def org_chart(request: HttpRequest) -> HttpResponse:
    employee: Employee = request.user.employee

    manager = employee.reporting_manager
    tree = None
    visible_employees: list[Employee] = []

    if employee.can_view_subtree():
        qs = employee.subtree_queryset()
        visible_employees = list(qs)
        tree = _build_tree(employee, visible_employees)
    else:
        # Regular employee: only see self + their manager
        visible_ids = [employee.id]
        if manager:
            visible_ids.append(manager.id)
        visible_employees = list(
            Employee.objects.filter(id__in=visible_ids).select_related("user", "reporting_manager")
        )

    return render(
        request,
        "org_chart.html",
        {
            "employee": employee,
            "manager": manager,
            "tree": tree,
            "visible_employees": visible_employees,
        },
    )


@admin_required
def admin_home(request: HttpRequest) -> HttpResponse:
    return render(request, "admin/admin_home.html", {"default_password": settings.HR_DEFAULT_PASSWORD})



@can_add_employees_required
def employee_list(request: HttpRequest) -> HttpResponse:
    current_employee = request.user.employee
    q = (request.GET.get("q") or "").strip()
    
    # HR Manager and HR Executive can see all employees
    if current_employee.can_access_admin_portal():
        qs = Employee.objects.select_related("user", "reporting_manager")
    else:
        # Other managers can only see their own subtree (team members)
        team_ids = current_employee.subtree_ids()
        qs = Employee.objects.filter(id__in=team_ids).select_related("user", "reporting_manager")
    
    if q:
        qs = qs.filter(models.Q(user__username__icontains=q) | models.Q(full_name__icontains=q))
    
    employees = qs.order_by("user__username")[:500]
    return render(request, "admin/employee_list.html", {"employees": employees, "q": q})


@can_add_employees_required
@require_http_methods(["GET", "POST"])
def employee_create(request: HttpRequest) -> HttpResponse:
    current_employee = request.user.employee
    form = EmployeeCreateForm(request.POST or None, current_user=current_employee)
    if request.method == "POST" and form.is_valid():
        employee = form.save()
        messages.success(request, f"Created employee {employee.employee_id}.")
        return redirect("employee_list")
    return render(request, "admin/employee_form.html", {"form": form, "mode": "create"})


@can_add_employees_required
@require_http_methods(["GET", "POST"])
def employee_edit(request: HttpRequest, pk: int) -> HttpResponse:
    current_employee = request.user.employee
    employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
    
    # Check if current user has permission to edit this employee
    if not current_employee.can_access_admin_portal():
        # Non-admin managers can only edit their team members
        if employee.id not in current_employee.subtree_ids():
            messages.error(request, "You don't have permission to edit this employee.")
            return redirect("employee_list")
    form = EmployeeUpdateForm(request.POST or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employee updated.")
        return redirect("employee_list")
    return render(
        request, "admin/employee_form.html", {"form": form, "mode": "edit", "employee_obj": employee}
    )


@can_add_employees_required
@require_http_methods(["GET", "POST"])
def employee_delete(request: HttpRequest, pk: int) -> HttpResponse:
    current_employee = request.user.employee
    employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
    
    if employee.user_id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect("employee_list")
    
    # Check if current user has permission to delete this employee
    if not current_employee.can_access_admin_portal():
        # Non-admin managers can only delete their team members
        if employee.id not in current_employee.subtree_ids():
            messages.error(request, "You don't have permission to delete this employee.")
            return redirect("employee_list")

    if request.method == "POST":
        employee.user.delete()
        messages.success(request, "Employee deleted.")
        return redirect("employee_list")

    return render(request, "admin/employee_confirm_delete.html", {"employee_obj": employee})


@can_add_employees_required
@require_http_methods(["GET", "POST"])
def employee_reset_password(request: HttpRequest, pk: int) -> HttpResponse:
    current_employee = request.user.employee
    employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
    
    # Check if current user has permission to reset password for this employee
    if not current_employee.can_access_admin_portal():
        # Non-admin managers can only reset passwords for their team members
        if employee.id not in current_employee.subtree_ids():
            messages.error(request, "You don't have permission to reset this employee's password.")
            return redirect("employee_list")
    if request.method == "POST":
        employee.user.set_password(settings.HR_DEFAULT_PASSWORD)
        employee.user.save(update_fields=["password"])
        employee.must_change_password = True
        employee.save(update_fields=["must_change_password"])
        messages.success(request, f"Password reset for {employee.employee_id}.")
        return redirect("employee_list")
    return render(
        request,
        "admin/employee_confirm_reset_password.html",
        {"employee_obj": employee, "default_password": settings.HR_DEFAULT_PASSWORD},
    )


@can_add_employees_required
@require_http_methods(["GET", "POST"])
def generate_offer_letter(request: HttpRequest) -> HttpResponse:
    """Generate offer letter and save for HR approval"""
    from django.core.files.base import ContentFile
    import secrets
    
    if request.method == "POST":
        form = OfferLetterForm(request.POST)
        if form.is_valid():
            from .models import OfferLetter
            
            # Prepare data for PDF generation
            data = form.cleaned_data.copy()
            # Get designation display name
            designation_choices = dict(Employee.Role.choices)
            data['designation_display'] = designation_choices.get(data['designation'], data['designation'])
            
            # Store original values before formatting
            original_offer_date = data['offer_date']
            original_joining_date = data['joining_date']
            original_salary = data['annual_salary']
            
            # Format for PDF
            data['offer_date'] = original_offer_date.strftime('%d-%m-%Y')
            data['joining_date'] = original_joining_date.strftime('%B %Y')
            data['annual_salary'] = f"{original_salary:,.2f}"
            
            # Generate PDF
            pdf_content = generate_offer_letter_pdf(data)
            
            # Create OfferLetter record
            offer_letter = OfferLetter(
                created_by=request.user.employee,
                candidate_name=form.cleaned_data['candidate_name'],
                candidate_email=form.cleaned_data.get('candidate_email', ''),
                designation=form.cleaned_data['designation'],
                designation_display=data['designation_display'],
                department=form.cleaned_data['department'],
                annual_salary=f"{original_salary:,.2f}",
                salary_in_words=form.cleaned_data['salary_in_words'],
                joining_date=original_joining_date.strftime('%B %Y'),
                offer_date=original_offer_date.strftime('%d-%m-%Y'),
                reference_number=form.cleaned_data['reference_number'],
                team_details=form.cleaned_data.get('team_details', ''),
                download_token=secrets.token_urlsafe(32),
                status='pending'
            )
            
            # Save PDF file
            filename = f"{form.cleaned_data['reference_number']}_{form.cleaned_data['candidate_name'].replace(' ', '_')}.pdf"
            offer_letter.pdf_file.save(filename, ContentFile(pdf_content), save=True)
            
            messages.success(
                request, 
                f"Offer letter for {form.cleaned_data['candidate_name']} has been submitted for HR approval."
            )
            return redirect("offer_letters_list")
    else:
        form = OfferLetterForm()
    
    return render(request, "offer_letter_form.html", {"form": form})


@employee_required
@require_http_methods(["GET", "POST"])
def submit_daily_report(request: HttpRequest) -> HttpResponse:
    """Submit or update daily work report"""
    current_employee = request.user.employee
    today = date.today()
    
    # Get or create today's report
    report, created = DailyReport.objects.get_or_create(
        employee=current_employee,
        report_date=today,
        defaults={'tasks_completed': ''}
    )
    
    if request.method == "POST":
        form = DailyReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Daily report submitted successfully!")
            return redirect("dashboard")
    else:
        form = DailyReportForm(instance=report)
    
    return render(request, "report_submit_form.html", {
        "form": form,
        "report_date": today,
        "is_update": not created
    })


@employee_required
def manager_reports_dashboard(request: HttpRequest) -> HttpResponse:
    """View daily reports from team members with filtering"""
    current_employee = request.user.employee
    
    # Get team members (excluding self)
    team_ids = current_employee.subtree_ids()
    team_ids.discard(current_employee.id)  # Remove self
    
    if not team_ids:
        return render(request, "manager_reports_dashboard.html", {
            "has_team": False,
            "message": "You don't have any team members to view reports for."
        })
    
    # Get filter parameters
    selected_date_str = request.GET.get('date', date.today().isoformat())
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()
    
    status_filter = request.GET.get('status', 'all')  # all, submitted, not_submitted
    
    # Get all team members
    team_members = Employee.objects.filter(id__in=team_ids).select_related('user')
    
    # Get reports for selected date
    reports = DailyReport.objects.filter(
        employee_id__in=team_ids,
        report_date=selected_date
    ).select_related('employee__user')
    
    # Create a dict of employee_id -> report
    reports_dict = {r.employee_id: r for r in reports}
    
    # Build list with submission status
    team_data = []
    for emp in team_members:
        report = reports_dict.get(emp.id)
        team_data.append({
            'employee': emp,
            'report': report,
            'has_submitted': report is not None
        })
    
    # Apply status filter
    if status_filter == 'submitted':
        team_data = [t for t in team_data if t['has_submitted']]
    elif status_filter == 'not_submitted':
        team_data = [t for t in team_data if not t['has_submitted']]
    
    # Calculate stats
    total_team = len(team_members)
    submitted_count = len([t for t in team_data if t['has_submitted']])
    
    return render(request, "manager_reports_dashboard.html", {
        "has_team": True,
        "team_data": team_data,
        "selected_date": selected_date,
        "status_filter": status_filter,
        "total_team": total_team,
        "submitted_count": submitted_count,
        "not_submitted_count": total_team - submitted_count,
    })


@employee_required
def view_report_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """View detailed daily report"""
    current_employee = request.user.employee
    report = get_object_or_404(DailyReport.objects.select_related('employee__user'), pk=pk)
    
    # Check permission: Can only view reports from team members
    team_ids = current_employee.subtree_ids()
    if report.employee_id not in team_ids:
        messages.error(request, "You don't have permission to view this report.")
        return redirect("manager_reports_dashboard")
    
    return render(request, "report_detail.html", {"report": report})


# ==================== OFFER LETTER APPROVAL WORKFLOW ====================

from django.http import FileResponse

@can_add_employees_required
def offer_letters_list(request):
    from .models import OfferLetter
    current_employee = request.user.employee
    offer_letters = OfferLetter.objects.filter(created_by=current_employee).order_by('-created_at')
    return render(request, 'offer_letters_list.html', {'offer_letters': offer_letters})

@admin_required
def hr_approval_dashboard(request):
    from .models import OfferLetter
    status_filter = request.GET.get('status', 'pending')
    if status_filter == 'all':
        offer_letters = OfferLetter.objects.all()
    else:
        offer_letters = OfferLetter.objects.filter(status=status_filter)
    offer_letters = offer_letters.select_related('created_by__user', 'approved_by__user').order_by('-created_at')
    pending_count = OfferLetter.objects.filter(status='pending').count()
    approved_count = OfferLetter.objects.filter(status='approved').count()
    rejected_count = OfferLetter.objects.filter(status='rejected').count()
    return render(request, 'hr_approval_dashboard.html', {
        'offer_letters': offer_letters, 'status_filter': status_filter, 
        'pending_count': pending_count, 'approved_count': approved_count, 'rejected_count': rejected_count
    })

@admin_required
@require_http_methods(['POST'])
def approve_offer_letter(request, pk):
    from .models import OfferLetter
    from django.utils import timezone
    offer_letter = get_object_or_404(OfferLetter, pk=pk)
    offer_letter.status = 'approved'
    offer_letter.approved_by = request.user.employee
    offer_letter.approved_at = timezone.now()
    offer_letter.save()
    messages.success(request, f'Offer letter for {offer_letter.candidate_name} has been approved.')
    return redirect('hr_approval_dashboard')

@admin_required
@require_http_methods(['POST'])
def reject_offer_letter(request, pk):
    from .models import OfferLetter
    offer_letter = get_object_or_404(OfferLetter, pk=pk)
    rejection_reason = request.POST.get('rejection_reason', 'No reason provided')
    offer_letter.status = 'rejected'
    offer_letter.rejection_reason = rejection_reason
    offer_letter.save()
    messages.warning(request, f'Offer letter for {offer_letter.candidate_name} has been rejected.')
    return redirect('hr_approval_dashboard')

@employee_required
def download_offer_letter(request, pk):
    from .models import OfferLetter
    offer_letter = get_object_or_404(OfferLetter, pk=pk)
    current_employee = request.user.employee
    can_download = (current_employee.can_access_admin_portal() or (offer_letter.created_by == current_employee and offer_letter.status == 'approved'))
    if not can_download:
        messages.error(request, 'You don\'t have permission to download this offer letter.')
        return redirect('offer_letters_list')
    return FileResponse(offer_letter.pdf_file, as_attachment=True, filename=f'Offer_Letter_{offer_letter.candidate_name}.pdf')

def candidate_download_page(request, token):
    from .models import OfferLetter
    offer_letter = get_object_or_404(OfferLetter, download_token=token)
    if offer_letter.status != 'approved':
        return render(request, 'candidate_download_error.html', {'message': 'This offer letter is pending approval and cannot be downloaded yet.'})
    if request.GET.get('download') == '1':
        return FileResponse(offer_letter.pdf_file, as_attachment=True, filename=f'Offer_Letter_{offer_letter.candidate_name}.pdf')
    return render(request, 'candidate_download_page.html', {'offer_letter': offer_letter})
