from django.contrib.auth.models import User
from org.models import Employee

# Reset password and disable forced password change
user = User.objects.get(username='1001')
user.set_password('Welcome@123')
user.save()

employee = user.employee
employee.must_change_password = False
employee.save()

print("✅ Password reset complete!")
print(f"   Username: {user.username}")
print(f"   Password: Welcome@123")
print(f"   Must change password: {employee.must_change_password}")
print(f"   Name: {employee.full_name}")
print(f"   Designation: {employee.get_role_display()}")
