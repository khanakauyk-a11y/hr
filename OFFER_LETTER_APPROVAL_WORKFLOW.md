# Offer Letter Approval Workflow - Complete

## ✅ Implementation Status: COMPLETE

All features of the offer letter approval workflow have been implemented.

---

## Overview

The offer letter system now requires HR approval before letters can be downloaded. This provides:
- ✅ Controlled distribution of offer letters
- ✅ Audit trail of all generated letters 
- ✅ HR oversight and quality control
- ✅ Secure candidate download via unique links

---

## User Flows

### For Managers (can_add_employees)

1. **Generate Offer Letter**
   - Navigate to "Generate Offer Letter"
   - Fill in candidate details including **email**
   - Submit form
   - System generates PDF and saves to database with status='pending'
   - **No immediate download** - manager sees success message
   - Redirected to "My Offer Letters" page

2. **Track Offer Letters**
   - View list of all generated offer letters
   - See status: Pending / Approved / Rejected
   - Download approved letters
   - View rejection reasons for rejected letters

### For HR (HR Manager / HR Executive)

1. **Review Pending Approvals**
   - Navigate to "Approve Offer Letters" (shows pending count badge)
   - View all pending offer letters
   - See candidate details, designation, created by, etc.

2. **Approve Offer Letter**
   - Click "Approve" button
   - System records approval timestamp and approver
   - Status changes to 'approved'
   - Creator can now download
   - Candidate can download via unique link

3. **Reject Offer Letter**
   - Click "Reject" button
   - Modal opens requesting rejection reason
   - Enter reason and confirm
   - Status changes to 'rejected'
   - Creator sees rejection status and reason

### For Candidates (No Login Required)

1. **Receive Download Link**
   - HR or creator shares unique link: `/offer/{token}/`
   - Example: `https://yourapp.com/offer/abc123xyz...`/

2. **Download Approved Letter**
   - Click link (no authentication needed)
   - See offer letter details
   - Click "Download Offer Letter (PDF)"
   - PDF downloads automatically

3. **If Not Approved**
   - See error message: "This offer letter is pending approval"
   - Cannot download until HR approves

---

## Database Schema

### OfferLetter Model

```python
class OfferLetter(models.Model):
    # Who created it
    created_by = ForeignKey(Employee)
    
    # Candidate information
    candidate_name = CharField(max_length=200)
    candidate_email = EmailField()
    designation = CharField(max_length=100)
    designation_display = CharField(max_length=200)
    department = CharField(max_length=100)
    annual_salary = CharField(max_length=50)
    salary_in_words = CharField(max_length=200)
    joining_date = CharField(max_length=50)
    offer_date = CharField(max_length=50)
    reference_number = CharField(max_length=100, unique=True)
    team_details = TextField(blank=True)
    
    # Approval workflow
    status = CharField(choices=['pending', 'approved', 'rejected'], default='pending')
    approved_by = ForeignKey(Employee, null=True, blank=True)
    approved_at = DateTimeField(null=True, blank=True)
    rejection_reason = TextField(blank=True)
    
    # File storage
    pdf_file = FileField(upload_to='offer_letters/')
    
    # Unique download token for candidate access
    download_token = CharField(max_length=64, unique=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

---

## API Endpoints

| URL | View | Permission | Method | Description |
|-----|------|------------|--------|-------------|
| `/offer-letter/generate/` | `generate_offer_letter` | can_add_employees | GET, POST | Generate new offer letter |
| `/offer-letters/` | `offer_letters_list` | can_add_employees | GET | List user's offer letters |
| `/offer-letters/approve/` | `hr_approval_dashboard` | HR only | GET | HR approval dashboard |
| `/offer-letters/<pk>/approve/` | `approve_offer_letter` | HR only | POST | Approve an offer letter |
| `/offer-letters/<pk>/reject/` | `reject_offer_letter` | HR only | POST | Reject an offer letter |
| `/offer-letters/<pk>/download/` | `download_offer_letter` | Creator/HR | GET | Download approved letter |
| `/offer/<token>/` | `candidate_download_page` | Public | GET | Candidate download page |

---

## Navigation

### For Managers
- **"Generate Offer Letter"** - Create new offer letters
- **"My Offer Letters"** - View and track all generated letters

### For HR
- **"Approve Offer Letters"** - Shows pending count badge
  - Filter by: Pending / Approved / Rejected / All
  - Approve or reject with one click
  - View all details

---

## File Storage

- **Location**: `media/offer_letters/`
- **Naming**: `{reference_number}_{candidate_name}.pdf`
- **Example**: `EOM_HR_DP_095_25_711_John_Doe.pdf`

### Production Deployment Notes:
- Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured
- For Railway: Media files are stored in ephemeral storage (lost on redeploy)
- **Recommended**: Use cloud storage (AWS S3, Cloudinary) for production
- For Railway with Cloudinary:
  ```python
  # settings.py
  DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
  ```

---

## Security

### Permissions Matrix

| Action | Manager | HR | Candidate |
|--------|---------|----|-----------| 
| Generate offer letter | ✅ | ✅ | ❌ |
| View own letters | ✅ | ✅ | ❌ |
| View all letters | ❌ | ✅ | ❌ |
| Approve/Reject | ❌ | ✅ | ❌ |
| Download approved (own) | ✅ | ✅ | ❌ |
| Download via token | ❌ | ❌ | ✅ |

### Token Security
- 256-bit random tokens using `secrets.token_urlsafe(32)`
- Tokens are unique and unpredictable
- No authentication required for candidate downloads
- Only approved letters can be downloaded

---

## Status Indicators

### In "My Offer Letters" (Manager View)

| Status | Badge Color | Download Button |
|--------|-------------|-----------------|
| Pending | Yellow/Warning | Disabled - "Awaiting HR approval" |
| Approved | Green/Success | Enabled - "Download" |
| Rejected | Red/Danger | Disabled - Shows rejection reason |

### In HR Dashboard

| Status | Badge Color | Actions |
|--------|-------------|---------|
| Pending | Yellow | Approve / Reject buttons |
| Approved | Green | Download only |
| Rejected | Red | Download only |

---

## Testing Checklist

### ✅ Generation Flow
- [x] Manager can generate offer letter
- [x] Form includes candidate email field
- [x] PDF is generated and saved
- [x] Status set to 'pending'
- [x] Unique token generated
- [x] Success message shown
- [x] Redirect to "My Offer Letters"

### ✅ Manager View
- [x] List shows all generated letters
- [x] Status badges display correctly
- [x] Download button only for approved  
- [x] Rejection reason visible for rejected

### ✅ HR Approval
- [x] Dashboard shows all letters
- [x] Filter by status works
- [x] Pending count badge in nav
- [x] Approve button changes status
- [x] Reject modal requests reason
- [x] Approver and timestamp recorded

### ✅ Candidate Download
- [x] Unique link works without login
- [x] Shows offer details
- [x] Download button works
- [x] Returns PDF file
- [x] Error page for pending/rejected

### ✅ Permissions
- [x] Only managers can generate
- [x] Only HR can approve/reject
- [x] Creators can download approved
- [x] HR can download any
- [x] Public token access works

---

## Migration

The migration `0005_simplify_roles.py` includes the `OfferLetter` model creation.

To apply:
```bash
python manage.py migrate
```

**Already applied if you ran migrations after role simplification.**

---

## Future Enhancements

### Suggested Improvements:
1. **Email Notifications**
   - Send email to candidate with download link after approval
   - Notify creator when approved/rejected
   
2. **Bulk Actions**
   - Approve multiple letters at once
   - Export to CSV

3. **Analytics**
   - Pending approvals aging report
   - Approval rate by HR user
   - Time-to-approval metrics

4. **Versioning**
   - Track revisions if offer is regenerated
   - Compare versions

5. **Templates**
   - Multiple offer letter templates
   - Department-specific templates

---

## Support

For questions or issues:
1. Check this documentation
2. Review the code in `org/views.py` (offer letter approval section)
3. Check templates: `offer_letters_list.html`, `hr_approval_dashboard.html`

---

**Status**: ✅ FULLY IMPLEMENTED  
**Last Updated**: January 5, 2026  
**Version**: 1.0
