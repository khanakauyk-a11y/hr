# 🚀 HR Portal - Quick Hostinger Deployment

## One-Command Setup ⚡

After uploading all files to Hostinger, just run:

```bash
bash setup_hostinger.sh
```

That's it! Your HR Portal will be automatically configured and ready to use.

---

## 📦 What This Package Contains

### Core Files:
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `passenger_wsgi.py` - Hostinger WSGI application entry point
- `.htaccess` - Apache/Passenger configuration
- `db.sqlite3` - Database (will be created during setup)

### Folders:
- `hr_portal/` - Django project settings
- `org/` - Main application (models, views, forms)
- `templates/` - HTML templates
- `staticfiles/` - Static files (CSS, JS, images) - created during setup
- `media/` - File uploads (offer letters) - created during setup

### Setup Scripts:
- `setup_hostinger.sh` - **Automated setup script** ✨
- `start.sh` - Application startup script

---

## 🎯 Upload & Deploy Instructions

### Step 1: Upload Files to Hostinger

**Via File Manager:**
1. Login to Hostinger Control Panel
2. Go to **File Manager**
3. Navigate to `domains/yourdomain.com/public_html`
4. Upload ALL files from this package
5. Extract if you uploaded as ZIP

**Via FTP:**
1. Use FileZilla or WinSCP
2. Connect with your Hostinger FTP credentials
3. Upload to `/public_html` folder

### Step 2: Access SSH Terminal

1. In Hostinger Control Panel, go to **Advanced** → **SSH Access**
2. Enable SSH if not already enabled
3. Connect via terminal:
   ```bash
   ssh your-username@yourdomain.com
   ```
4. Navigate to your project:
   ```bash
   cd domains/yourdomain.com/public_html
   ```

### Step 3: Run Automated Setup

```bash
bash setup_hostinger.sh
```

The script will automatically:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Configure WSGI with correct paths
- ✅ Update Apache configuration
- ✅ Create media directories
- ✅ Run database migrations
- ✅ Collect static files

### Step 4: Create Admin User (Optional)

```bash
source ~/python-env/bin/activate
python manage.py createsuperuser
```

Or use the default admin:
- **Employee ID:** 1001
- **Password:** Welcome@123

### Step 5: Access Your Website

Visit your domain: `https://yourdomain.com`

The HR Portal should now be live! 🎉

---

## 🔧 Manual Configuration (If Automatic Setup Fails)

If the automated script doesn't work, follow these steps:

### 1. Create Virtual Environment
```bash
cd ~
python3 -m venv python-env
source python-env/bin/activate
```

### 2. Install Dependencies
```bash
cd ~/domains/yourdomain.com/public_html
pip install -r requirements.txt
```

### 3. Update `passenger_wsgi.py`
Edit the file and replace:
- `YOUR_USERNAME` with your Hostinger username (e.g., `u123456789`)
- `YOUR_DOMAIN.com` with your actual domain

### 4. Update `.htaccess`
Same as above - replace placeholders with your actual paths.

### 5. Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. Restart Application
```bash
mkdir -p tmp
touch tmp/restart.txt
```

---

## 🗄️ Database Options

### SQLite (Default - Already Configured)
- No additional setup needed
- Perfect for small to medium usage
- Database file: `db.sqlite3`

### MySQL (For Production)
1. Create MySQL database in Hostinger panel
2. Update `hr_portal/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```
3. Run migrations again

---

## 📁 Directory Structure After Upload

```
public_html/
├── hr_portal/          # Django settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── org/                # Main app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
├── templates/          # HTML templates
├── staticfiles/        # CSS, JS (created by collectstatic)
├── media/              # Uploaded files (created automatically)
│   └── offer_letters/
├── manage.py
├── passenger_wsgi.py   # WSGI entry point
├── .htaccess          # Apache config
├── requirements.txt
├── setup_hostinger.sh # Auto-setup script
└── db.sqlite3         # Database (created)
```

---

## 🔑 Default Login Credentials

After setup, you can login using:

**Admin/HR Manager:**
- Employee ID: `1001`
- Password: `Welcome@123`

**Change password after first login!**

---

## ✅ Post-Deployment Checklist

- [ ] Website loads without errors
- [ ] Can login with default credentials
- [ ] Static files (CSS) are loading correctly
- [ ] Navigation works
- [ ] Can access admin portal
- [ ] Can generate offer letters
- [ ] Daily reports feature works
- [ ] SSL certificate installed (HTTPS)

---

## 🆘 Troubleshooting

### Issue: "Internal Server Error"

**Check error logs:**
```bash
tail -f ~/logs/error_log
```

**Common fixes:**
```bash
# Restart application
touch tmp/restart.txt

# Check permissions
chmod -R 755 .
chmod 644 *.py
```

### Issue: "Static files not loading"

```bash
python manage.py collectstatic --clear --noinput
chmod -R 755 staticfiles/
```

### Issue: "Module not found"

```bash
source ~/python-env/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Issue: "Database locked"

```bash
# If using SQLite
chmod 664 db.sqlite3
chmod 775 .
```

---

## 🔄 Updating Your Application

When you make changes:

```bash
# Connect via SSH
cd ~/domains/yourdomain.com/public_html

# Activate virtual environment
source ~/python-env/bin/activate

# Pull latest code (if using git)
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
touch tmp/restart.txt
```

---

## 📞 Support

**Hostinger Support:**
- Live Chat: 24/7 available in control panel
- Knowledge Base: https://support.hostinger.com

**HR Portal Documentation:**
- See `HOSTINGER_DEPLOYMENT.md` for detailed guide
- Check `README.md` for feature documentation

---

## 🎉 You're All Set!

Your HR Portal is now deployed on Hostinger!

**Access your portal at:** `https://yourdomain.com`

**Features Available:**
- ✅ Employee Management
- ✅ Daily Reporting System
- ✅ Offer Letter Generation
- ✅ Team Analytics
- ✅ Role-Based Access Control

---

**Need help?** Check the detailed deployment guide in `HOSTINGER_DEPLOYMENT.md`
