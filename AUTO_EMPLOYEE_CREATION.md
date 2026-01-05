# Auto-Employee Creation on Offer Letter Approval

## Overview

When HR approves an offer letter, the system **automatically creates an Employee record** and adds them to the organizational hierarchy.

---

## How It Works

### **Workflow:**

```
Manager generates offer letter
         ↓
    HR approves
         ↓
✨ AUTOMATIC EMPLOYEE CREATION ✨
         ↓
Employee appears in org tree
```

---

## What Happens When HR Clicks "Approve"

### 1. **Employee ID Generation**
- System finds the highest existing employee ID
- Increments by 1 to create new unique ID
- Example: Last ID = 1006 → New ID = 1007

### 2. **User Account Creation**
- **Username:** Same as Employee ID (e.g., `1007`)
- **Password:** `Welcome@123` (from `HR_DEFAULT_PASSWORD` setting)
- **First Name:** Extracted from candidate name
- **Last Name:** Remaining part of name

### 3. **Employee Record Creation**
- **Employee ID:** Auto-generated (e.g., `1007`)
- **Full Name:** From offer letter
- **Email:** From offer letter
- **Role/Designation:** From offer letter (e.g., Assistant Manager)
- **Reporting Manager:** The person who created the offer letter
- **Date of Joining:** Current date

### 4. **Organizational Tree Update**
- Employee automatically appears under their manager
- Visible immediately in org chart
- Counted in manager's team

---

## Success Message

After approval, HR sees:

```
✅ Offer letter approved! Employee John Doe (ID: 1007) has been added under Sales Manager.
```

---

## Employee Login

The new employee can now login with:
- **Username:** Their Employee ID (e.g., `1007`)
- **Password:** `Welcome@123`

They should change their password on first login.

---

## Example Scenario

### Before Approval:
- **Sales Manager (ID: 1002)** generates offer letter for **"Khan"**
- Designation: **Assistant Manager**
- Email: `khan@example.com`

### After HR Approves:
1. **New Employee Created:**
   - Employee ID: `1007` (auto-generated)
   - Name: Khan
   - Role: Assistant Manager
   - Reports to: Sales Manager (1002)

2. **Org Tree Updated:**
   ```
   Sales Manager (1002)
   └── Khan (1007) - Assistant Manager
   ```

3. **Khan can login:**
   - Username: `1007`
   - Password: `Welcome@123`

---

## Duplicate Prevention

If you try to approve an already-approved offer letter:
- ❌ **No duplicate employee** is created
- ⚠️ Warning message shown
- ✅ Original employee record remains unchanged

---

## Database Transaction Safety

The employee creation process uses **atomic transactions**:
- All steps happen together or none happen
- If any error occurs, database rolls back
- No partial/corrupted employee records

---

## Error Handling

If employee creation fails:
- Error message is shown to HR
- Offer letter remains unapproved
- No changes to database
- HR can try again or fix the issue

---

## Benefits

### ✅ **For HR:**
- No manual employee creation needed
- Automatic ID generation
- Instant org chart update
- One-click approval process

### ✅ **For Managers:**
- New team member appears automatically
- Can see them in org tree immediately
- No waiting for HR to manually add employee

### ✅ **For New Employees:**
- Ready-to-use login credentials
- Immediate system access
- Part of team from day one

---

## Important Notes

1. **Employee ID Format:**
   - Must be numeric for auto-increment to work
   - Starts from 1007 if no numeric IDs exist
   - Sequential (1007, 1008, 1009...)

2. **Default Password:**
   - Set in `settings.HR_DEFAULT_PASSWORD`
   - Currently: `Welcome@123`
   - Employees should change on first login

3. **Reporting Structure:**
   - New employee reports to offer letter creator
   - Cannot be changed during approval
   - Can be updated later via "Manage Employees"

4. **Role Assignment:**
   - Role comes from offer letter designation
   - Must match one of the system roles
   - Determines permissions and hierarchy

---

## Testing Checklist

- [ ] Generate offer letter as manager
- [ ] HR approves the offer letter
- [ ] New employee ID is sequential
- [ ] Employee appears in org tree
- [ ] Employee can login with auto-generated credentials
- [ ] Employee is under correct manager
- [ ] Duplicate approval shows warning
- [ ] Error handling works if fields are invalid

---

## Future Enhancements

Potential improvements:
1. **Email notification** to new employee with login details
2. **Custom employee ID format** (e.g., EMP-001, EOM-001)
3. **Multiple approvers** (HR + Department Head)
4. **Onboarding checklist** auto-created
5. **Welcome email** with company info

---

**Status:** ✅ IMPLEMENTED  
**Last Updated:** January 5, 2026  
**Version:** 1.0
