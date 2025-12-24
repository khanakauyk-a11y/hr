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

from .decorators import admin_required, employee_required
from .forms import EmployeeCreateForm, EmployeeIdAuthenticationForm, EmployeeUpdateForm
from .models import Employee


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
        return {"employee": emp, "children": children}

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


@admin_required
def employee_list(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get("q") or "").strip()
    qs = Employee.objects.select_related("user", "reporting_manager")
    if q:
        qs = qs.filter(models.Q(user__username__icontains=q) | models.Q(full_name__icontains=q))
    employees = qs.order_by("user__username")[:500]
    return render(request, "admin/employee_list.html", {"employees": employees, "q": q})


@admin_required
@require_http_methods(["GET", "POST"])
def employee_create(request: HttpRequest) -> HttpResponse:
    form = EmployeeCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        employee = form.save()
        messages.success(request, f"Created employee {employee.employee_id}.")
        return redirect("employee_list")
    return render(request, "admin/employee_form.html", {"form": form, "mode": "create"})


@admin_required
@require_http_methods(["GET", "POST"])
def employee_edit(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
    form = EmployeeUpdateForm(request.POST or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employee updated.")
        return redirect("employee_list")
    return render(
        request, "admin/employee_form.html", {"form": form, "mode": "edit", "employee_obj": employee}
    )


@admin_required
@require_http_methods(["GET", "POST"])
def employee_delete(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
    if employee.user_id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect("employee_list")

    if request.method == "POST":
        employee.user.delete()
        messages.success(request, "Employee deleted.")
        return redirect("employee_list")

    return render(request, "admin/employee_confirm_delete.html", {"employee_obj": employee})


@admin_required
@require_http_methods(["GET", "POST"])
def employee_reset_password(request: HttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
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
