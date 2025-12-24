from __future__ import annotations

from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def employee_required(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = request.user
        if not user.is_authenticated:
            return redirect("login")

        if not hasattr(user, "employee"):
            logout(request)
            messages.error(request, "No employee profile found for this account.")
            return redirect("login")

        if not user.employee.is_active:
            logout(request)
            messages.error(request, "This account is inactive.")
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return _wrapped


def admin_required(view_func):
    @wraps(view_func)
    @employee_required
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.employee.can_access_admin_portal():
            return view_func(request, *args, **kwargs)
        return redirect("dashboard")

    return _wrapped


