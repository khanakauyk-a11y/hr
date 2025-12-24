from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from org.models import Employee


class Command(BaseCommand):
    help = "Create an initial ADMIN employee account for the HR Portal."

    def add_arguments(self, parser):
        parser.add_argument("--employee-id", required=True, help="Employee ID used for login (stored as username).")
        parser.add_argument("--name", required=True, help="Full name for the employee profile.")
        parser.add_argument(
            "--password",
            default="",
            help="Optional password. If omitted, uses HR_DEFAULT_PASSWORD and forces change on first login.",
        )
        parser.add_argument(
            "--no-superuser",
            action="store_true",
            help="Do not mark this account as Django superuser/staff (portal admin still works).",
        )

    def handle(self, *args, **options):
        employee_id: str = options["employee_id"].strip()
        name: str = options["name"].strip()
        password: str = (options.get("password") or "").strip()
        make_superuser = not bool(options.get("no_superuser"))

        if not employee_id:
            raise CommandError("--employee-id is required")
        if not name:
            raise CommandError("--name is required")

        if User.objects.filter(username=employee_id).exists():
            raise CommandError(f"User '{employee_id}' already exists.")

        if not password:
            password = settings.HR_DEFAULT_PASSWORD
            must_change = True
        else:
            must_change = False

        user = User.objects.create_user(username=employee_id, password=password)
        if make_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["is_staff", "is_superuser"])

        Employee.objects.create(
            user=user,
            full_name=name,
            role=Employee.Role.ADMIN,
            reporting_manager=None,
            must_change_password=must_change,
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(f"Created ADMIN employee '{employee_id}'."))


