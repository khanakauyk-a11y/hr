from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Employee(models.Model):
    class Role(models.TextChoices):
        # Sales Designations
        SENIOR_SALES_MANAGER = "SENIOR_SALES_MANAGER", "Senior Sales Manager"
        SALES_MANAGER = "SALES_MANAGER", "Sales Manager"
        ASSISTANT_SALES_MANAGER = "ASSISTANT_SALES_MANAGER", "Assistant Sales Manager"
        SALES_EXECUTIVE = "SALES_EXECUTIVE", "Sales Executive"
        
        # Agent Designations
        AGENT_RELATIONSHIP_MANAGER = "AGENT_RELATIONSHIP_MANAGER", "Agent Relationship Manager"
        AGENT_MANAGER = "AGENT_MANAGER", "Agent Manager"
        AGENT = "AGENT", "Agent"
        
        # HR Designations
        HR_MANAGER = "HR_MANAGER", "HR Manager"
        HR_EXECUTIVE = "HR_EXECUTIVE", "HR Executive"
        
        # Management Designations
        ASSISTANT_GENERAL_MANAGER = "ASSISTANT_GENERAL_MANAGER", "Assistant General Manager"
        
        # Support Designations
        SENIOR_RETAINER = "SENIOR_RETAINER", "Senior Retainer"
        TELE_CALLER = "TELE_CALLER", "Tele Caller"
        TRAINER = "TRAINER", "Trainer"
        
        # IT Designations
        IT_MANAGER = "IT_MANAGER", "IT Manager"
        IT_EXECUTIVE = "IT_EXECUTIVE", "IT Executive"
        IT_GRAPHIC_DESIGNER = "IT_GRAPHIC_DESIGNER", "IT Graphic Designer"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.AGENT)

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
        """Only HR Manager and HR Executive can access the admin portal"""
        return self.role in {self.Role.HR_MANAGER, self.Role.HR_EXECUTIVE}

    def can_view_subtree(self) -> bool:
        """Manager-level positions can view their organizational subtree"""
        return self.role in {
            self.Role.SENIOR_SALES_MANAGER,
            self.Role.SALES_MANAGER,
            self.Role.ASSISTANT_SALES_MANAGER,
            self.Role.AGENT_RELATIONSHIP_MANAGER,
            self.Role.AGENT_MANAGER,
            self.Role.HR_MANAGER,
            self.Role.HR_EXECUTIVE,
            self.Role.ASSISTANT_GENERAL_MANAGER,
            self.Role.IT_MANAGER,
        }
    
    def can_add_employees(self) -> bool:
        """Designations with employee management permissions"""
        return self.role in {
            # Sales Management
            self.Role.SENIOR_SALES_MANAGER,
            self.Role.SALES_MANAGER,
            self.Role.ASSISTANT_SALES_MANAGER,
            self.Role.SALES_EXECUTIVE,  # Added
            
            # Agent Management
            self.Role.AGENT_RELATIONSHIP_MANAGER,
            self.Role.AGENT_MANAGER,
            
            # HR
            self.Role.HR_MANAGER,
            self.Role.HR_EXECUTIVE,
            
            # General Management
            self.Role.ASSISTANT_GENERAL_MANAGER,
            
            # Support
            self.Role.SENIOR_RETAINER,  # Added
            
            # IT Management & Staff
            self.Role.IT_MANAGER,
            self.Role.IT_EXECUTIVE,  # Added
            self.Role.IT_GRAPHIC_DESIGNER,  # Added
        }

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
    
    def has_team_members(self) -> bool:
        """Check if this employee has any team members (direct or indirect reports)"""
        return len(self.subtree_ids()) > 1  # More than just themselves

    def default_password(self) -> str:
        return getattr(settings, "HR_DEFAULT_PASSWORD", "Welcome@123")


class DailyReport(models.Model):
    """Daily work report submitted by employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField(default=timezone.now)
    tasks_completed = models.TextField(help_text="What tasks did you complete today?")
    challenges = models.TextField(blank=True, help_text="Any challenges or blockers faced?")
    next_day_plan = models.TextField(blank=True, help_text="What do you plan to work on tomorrow?")
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['employee', 'report_date']]
        ordering = ['-report_date', 'employee']
        verbose_name = "Daily Report"
        verbose_name_plural = "Daily Reports"
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.report_date}"
