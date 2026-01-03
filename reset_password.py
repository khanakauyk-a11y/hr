from django.contrib.auth.models import User
from org.models import Employee

print("=== All Users in Database ===")
for user in User.objects.all():
    emp = None
    if hasattr(user, 'employee'):
        emp = user.employee
        print(f"Username: {user.username}")
        print(f"  Name: {emp.full_name}")
        print(f"  Designation: {emp.get_role_display()}")
        print(f"  Active: {emp.is_active}")
        print()

print(f"Total users: {User.objects.count()}")
print("\n=== Resetting password for user 1001 ===")

# Reset password for user 1001
try:
    user = User.objects.get(username='1001')
    user.set_password('Welcome@123')
    user.save()
    print("✅ Password reset to: Welcome@123")
    print(f"   Username: {user.username}")
except User.DoesNotExist:
    print("❌ User 1001 not found! Creating new admin...")
    # Create if doesn't exist
    user = User.objects.create_user(username='1001', password='Welcome@123')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    Employee.objects.create(
        user=user,
        full_name="HR Admin",
        role=Employee.Role.HR_MANAGER,
        reporting_manager=None,
        must_change_password=False,
        is_active=True,
    )
    print("✅ Created new admin user 1001 with password: Welcome@123")
