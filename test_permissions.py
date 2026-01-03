from org.models import Employee

# Test permissions for newly added roles
test_roles = [
    ('SALES_EXECUTIVE', 'Sales Executive'),
    ('SENIOR_RETAINER', 'Senior Retainer'),
    ('IT_EXECUTIVE', 'IT Executive'),
    ('IT_GRAPHIC_DESIGNER', 'IT Graphic Designer'),
    ('AGENT', 'Agent'),
    ('TELE_CALLER', 'Tele Caller'),
    ('TRAINER', 'Trainer'),
]

print("=" * 60)
print("EMPLOYEE MANAGEMENT PERMISSIONS TEST")
print("=" * 60)

for role_value, role_display in test_roles:
    # Create a temporary employee instance to test
    temp_emp = Employee(role=role_value)
    can_add = temp_emp.can_add_employees()
    status = "✅ CAN" if can_add else "❌ CANNOT"
    print(f"{status} add employees: {role_display}")

print("=" * 60)
