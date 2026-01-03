# Permission Testing Examples

## Test Results - Designation Permissions

### Test 1: HR Manager (Employee ID: 1001)
```
Employee: HR Admin
Designation: HR Manager
✅ Can access admin portal: True
✅ Can add employees: True
✅ Can view subtree: True
```

### Test 2: Sales Manager (Employee ID: 10012)
```
Employee: umar
Designation: Sales Manager
❌ Can access admin portal: False
✅ Can add employees: True
✅ Can view subtree: True
```

### Expected Results for Other Designations

#### Manager-Level Designations (Can Manage):
- Senior Sales Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal
- Sales Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal
- Assistant Sales Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal
- Agent Relationship Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal
- Agent Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal
- HR Manager: ✅ Add Employees, ✅ View Subtree, ✅ Admin Portal
- HR Executive: ✅ Add Employees, ✅ View Subtree, ✅ Admin Portal
- Assistant General Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal
- IT Manager: ✅ Add Employees, ✅ View Subtree, ❌ Admin Portal

#### Regular Employee Designations (Cannot Manage):
- Sales Executive: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal
- Agent: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal
- Senior Retainer: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal
- Tele Caller: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal
- Trainer: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal
- IT Executive: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal
- IT Graphic Designer: ❌ Add Employees, ❌ View Subtree, ❌ Admin Portal

## What This Means

### If you login as a Manager (e.g., Sales Manager):
✅ You will see "Manage Employees" button in navigation
✅ You can add/edit/delete employees
✅ You can view your organizational subtree
❌ You cannot access Admin Portal (unless HR role)

### If you login as a Regular Employee (e.g., Agent):
❌ You will NOT see "Manage Employees" button
❌ Attempting to directly access `/admin/employees/` will show permission error
✅ You can still view your own dashboard
✅ You can see org chart (yourself + your manager)
✅ You can change your password

## Security Features

1. **Template-level protection**: Navigation links only shown to authorized users
2. **Decorator protection**: Views check permissions before allowing access
3. **Model-level logic**: Permissions defined in the Employee model
4. **Error messages**: Users without permission see friendly error message

## Testing Commands

To test any employee's permissions:
```bash
python manage.py shell -c "from org.models import Employee; emp = Employee.objects.get(user__username='EMPLOYEE_ID'); print(f'{emp.full_name}: Admin={emp.can_access_admin_portal()}, Manage={emp.can_add_employees()}, Subtree={emp.can_view_subtree()}')"
```

Replace `EMPLOYEE_ID` with the actual employee ID.
