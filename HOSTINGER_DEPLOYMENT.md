# Deploying HR Portal to Hostinger - Complete Guide

## Prerequisites
- Hostinger hosting account with Python support
- Domain name (optional, you can use Hostinger's subdomain)
- Your project code ready

---

## Step 1: Prepare Your Application

### 1.1 Update settings.py for Production

Add your Hostinger domain to `ALLOWED_HOSTS`:

```python
# In hr_portal/settings.py
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'your-domain.com',  # Add your actual domain
    'www.your-domain.com',
    '*.hostinger.com',  # If using Hostinger subdomain
]
```

### 1.2 Ensure Static Files Configuration

Make sure these are in `settings.py`:

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 1.3 Create .htaccess File

Create `.htaccess` in your project root:

```apache
# Force HTTPS (if you have SSL)
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Passenger Configuration
PassengerEnabled on
PassengerPython /home/username/python-env/bin/python
PassengerAppRoot /home/username/hr_portal
PassengerStartupFile passenger_wsgi.py
```

---

## Step 2: Create passenger_wsgi.py

This is the entry point for Hostinger's Python hosting. Create `passenger_wsgi.py` in your project root:

```python
import os
import sys

# Add your project directory to the sys.path
project_home = '/home/username/hr_portal'  # Change 'username' to your actual username
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'hr_portal.settings'

# Activate virtual environment
activate_env = os.path.expanduser("/home/username/python-env/bin/activate_this.py")
exec(open(activate_env).read(), {'__file__': activate_env})

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## Step 3: Upload Files to Hostinger

### 3.1 Via File Manager (Easy Method)

1. Login to **Hostinger Control Panel**
2. Go to **File Manager**
3. Navigate to `public_html` or your domain folder
4. Upload all your project files EXCEPT:
   - `.git/` folder
   - `db.sqlite3` (you'll create new one)
   - `__pycache__/` folders
   - `.env` files with secrets

### 3.2 Via FTP (Recommended)

1. Get FTP credentials from Hostinger
2. Use FileZilla or WinSCP
3. Upload entire project folder

**FTP Settings:**
- Host: Your domain or Hostinger FTP address
- Username: From Hostinger panel
- Password: From Hostinger panel
- Port: 21 (or 22 for SFTP)

---

## Step 4: Set Up Python Environment on Hostinger

### 4.1 Access SSH Terminal

1. Go to **Hostinger Control Panel**
2. Navigate to **Advanced** → **SSH Access**
3. Enable SSH if not already enabled
4. Use terminal or PuTTY to connect:

```bash
ssh username@your-domain.com
```

### 4.2 Create Virtual Environment

```bash
# Navigate to your home directory
cd ~

# Create virtual environment
python3 -m venv python-env

# Activate it
source python-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4.3 Install Dependencies

```bash
# Navigate to your project
cd hr_portal

# Install requirements
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn
pip install whitenoise  # For serving static files
```

---

## Step 5: Configure Database

### Option A: SQLite (Simple, for testing)

```bash
# In your project directory
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Option B: MySQL (Recommended for Production)

1. **Create MySQL Database in Hostinger:**
   - Go to **Databases** → **MySQL Databases**
   - Create new database
   - Create database user
   - Note: database name, username, password, host

2. **Update settings.py:**

```python
# In settings.py, replace DATABASES with:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',  # or your MySQL host
        'PORT': '3306',
    }
}
```

3. **Install MySQL client:**

```bash
pip install mysqlclient
```

4. **Run migrations:**

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## Step 6: Configure Static Files with WhiteNoise

### 6.1 Update settings.py

```python
# Add to MIDDLEWARE (after SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]

# Add at the bottom
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 6.2 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Step 7: Set Environment Variables

Create `.env` file in your project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=mysql://user:password@localhost/dbname
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

**Get your SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Step 8: Update passenger_wsgi.py with Your Paths

Replace `username` with your actual Hostinger username:

```python
import os
import sys

# CHANGE THIS to your actual path
project_home = '/home/u123456789/domains/your-domain.com/public_html/hr_portal'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'hr_portal.settings'

# CHANGE THIS to your virtual environment path
activate_env = '/home/u123456789/python-env/bin/activate_this.py'
exec(open(activate_env).read(), {'__file__': activate_env})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## Step 9: Restart Application

In Hostinger control panel or via SSH:

```bash
# Restart using touch
touch ~/public_html/tmp/restart.txt

# Or kill Python processes
pkill python
```

---

## Step 10: Test Your Deployment

1. Visit your domain: `https://your-domain.com`
2. Try logging in with the superuser you created
3. Test all features

---

## Common Issues & Solutions

### Issue 1: 500 Internal Server Error

**Check error logs:**
```bash
tail -f ~/logs/error_log
```

**Common causes:**
- Wrong paths in `passenger_wsgi.py`
- Missing dependencies
- Database connection error
- Wrong file permissions

### Issue 2: Static Files Not Loading

```bash
# Collect static files again
python manage.py collectstatic --clear --noinput

# Check permissions
chmod -R 755 staticfiles/
```

### Issue 3: Database Errors

```bash
# Verify database settings
python manage.py check --database default

# Run migrations again
python manage.py migrate
```

### Issue 4: Module Not Found

```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

---

## Post-Deployment Checklist

- [ ] Application loads without errors
- [ ] Admin login works
- [ ] Static files (CSS/JS) are loading
- [ ] Media files upload location works
- [ ] Database is accessible
- [ ] All features tested
- [ ] SSL certificate installed (HTTPS)
- [ ] Backups configured

---

## Maintenance Commands

### Update Code
```bash
cd ~/hr_portal
git pull origin main  # If using git
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch ~/public_html/tmp/restart.txt
```

### Backup Database

**For SQLite:**
```bash
cp db.sqlite3 db.sqlite3.backup-$(date +%Y%m%d)
```

**For MySQL:**
```bash
mysqldump -u username -p database_name > backup-$(date +%Y%m%d).sql
```

---

## Quick Deployment Script

Save as `deploy.sh`:

```bash
#!/bin/bash
echo "Deploying HR Portal..."

# Activate virtual environment
source ~/python-env/bin/activate

# Pull latest code (if using git)
# git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
touch ~/public_html/tmp/restart.txt

echo "Deployment complete!"
```

Make executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Support

**Hostinger Support:**
- Live Chat: Available 24/7
- Tutorials: https://support.hostinger.com

**Django Documentation:**
- Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

---

**Note:** Replace all `username`, `your-domain.com`, and paths with your actual Hostinger details!
