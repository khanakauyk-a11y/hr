from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Employee(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        TEAM_LEAD = "TEAM_LEAD", "Team Lead"
        EMPLOYEE = "EMPLOYEE", "Employee"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)

    # The person this employee reports to (can be null for top-level / admin accounts)
    reporting_manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="direct_reports",
    )

    must_change_password = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.full_name}"

    @property
    def employee_id(self) -> str:
        # We treat Django's username as the Employee ID for login.
        return self.user.username

    def clean(self):
        super().clean()

        if self.reporting_manager_id and self.reporting_manager_id == self.id:
            raise ValidationError({"reporting_manager": "Employee cannot report to themselves."})

        # Prevent cycles: A -> B -> C -> A
        if self.reporting_manager_id and self.id:
            seen_ids: set[int] = {self.id}
            cursor = self.reporting_manager
            while cursor is not None:
                if cursor.id in seen_ids:
                    raise ValidationError(
                        {"reporting_manager": "Invalid reporting manager (would create a cycle)."}
                    )
                seen_ids.add(cursor.id)
                cursor = cursor.reporting_manager

    def can_access_admin_portal(self) -> bool:
        return self.role == self.Role.ADMIN

    def can_view_subtree(self) -> bool:
        return self.role in {self.Role.MANAGER, self.Role.TEAM_LEAD}

    def subtree_ids(self) -> set[int]:
        """
        Returns ids for this employee + all (direct + indirect) reports.
        BFS; OK for small/medium orgs. For very large orgs, use a closure table.
        """
        root_id = self.id
        if root_id is None:
            return set()

        visited: set[int] = {root_id}
        frontier: set[int] = {root_id}

        while frontier:
            children = (
                Employee.objects.filter(reporting_manager_id__in=frontier)
                .values_list("id", flat=True)
                .iterator()
            )
            next_frontier: set[int] = set()
            for cid in children:
                if cid not in visited:
                    visited.add(cid)
                    next_frontier.add(cid)
            frontier = next_frontier

        return visited

    def subtree_queryset(self):
        return Employee.objects.filter(id__in=self.subtree_ids()).select_related("user", "reporting_manager")

    def default_password(self) -> str:
        return getattr(settings, "HR_DEFAULT_PASSWORD", "Welcome@123")
