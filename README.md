## HR Portal (Django)

This is a simple HR portal with:
- **Two login pages**: **Admin Login** (`/admin-login/`) and **User Login** (`/login/`)
- **Admin role** can **add / edit / delete** employees, assign **reporting manager**, and **reset passwords**
- **Hierarchy visibility**
  - **Manager / Team Lead** can see **their own subtree** (direct + indirect reports)
  - **Normal employee** sees **self + reporting manager**
- **Default password** for new users (configurable)

---

## Local setup (Windows)

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_admin --employee-id 1001 --name "HR Admin"
python manage.py runserver
```

Open:
- Home: `http://127.0.0.1:8000/`
- Admin login: `http://127.0.0.1:8000/admin-login/`
- User login: `http://127.0.0.1:8000/login/`
- Optional Django admin: `http://127.0.0.1:8000/dj-admin/`

Default password is **`Welcome@123`** (change via env var `HR_DEFAULT_PASSWORD`).

---

## How to create employees

1. Login as admin: `/admin-login/`
2. Go to **Admin Portal → Manage Employees**
3. Add employees:
   - **Employee ID** becomes the login ID
   - Choose **Role**: Employee / Team Lead / Manager / Admin
   - Set **Reporting manager** to build the org hierarchy

---

## Hosting on Hostinger

Hostinger **Shared Hosting** usually cannot run Django (no persistent WSGI process).
Use **Hostinger VPS** (recommended) or any Linux VPS.

### VPS (Gunicorn + systemd + Nginx) — copy/paste guide

Assumptions:
- VPS OS: **Ubuntu 22.04/24.04** (similar for Debian)
- Domain: `yourdomain.com`
- Project path: `/var/www/hr_portal`

#### 1) Connect to VPS + install packages

1. SSH into VPS, install dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx
```

#### 2) Upload your code
Option A (recommended): push to GitHub, then on VPS:

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone YOUR_GIT_REPO_URL hr_portal
sudo chown -R $USER:$USER /var/www/hr_portal
```

Option B: upload via SFTP to `/var/www/hr_portal`.

#### 3) Create venv + install dependencies

```bash
cd /var/www/hr_portal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 4) Set environment variables
Create `/var/www/hr_portal/.env`:

```bash
nano /var/www/hr_portal/.env
```

Example contents (edit the domain + secret):

```bash
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=change-this-to-a-long-random-secret
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
HR_DEFAULT_PASSWORD=Welcome@123
```

#### 5) Migrate + collect static + create first admin

```bash
cd /var/www/hr_portal
source .venv/bin/activate
set -a && source .env && set +a
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py bootstrap_admin --employee-id 1001 --name "HR Admin"
```

#### 6) Create a systemd service for Gunicorn
Create `/etc/systemd/system/hr_portal.service`:

```bash
sudo nano /etc/systemd/system/hr_portal.service
```

Paste this (edit `User=` if needed):

```ini
[Unit]
Description=HR Portal (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hr_portal
EnvironmentFile=/var/www/hr_portal/.env
ExecStart=/var/www/hr_portal/.venv/bin/gunicorn hr_portal.wsgi:application --bind 127.0.0.1:8001 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable + start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hr_portal
sudo systemctl start hr_portal
sudo systemctl status hr_portal --no-pager
```

#### 7) Configure Nginx (reverse proxy + static files)
Create `/etc/nginx/sites-available/hr_portal`:

```bash
sudo nano /etc/nginx/sites-available/hr_portal
```

Paste (edit domain):

```nginx
server {
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /var/www/hr_portal/staticfiles/;
        expires 30d;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_pass http://127.0.0.1:8001;
    }
}
```

Enable site + reload:

```bash
sudo ln -sf /etc/nginx/sites-available/hr_portal /etc/nginx/sites-enabled/hr_portal
sudo nginx -t
sudo systemctl reload nginx
```

#### 8) HTTPS (Let’s Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### 9) Useful troubleshooting commands

```bash
sudo systemctl status hr_portal --no-pager
sudo journalctl -u hr_portal -n 200 --no-pager
sudo nginx -t
```

---

## Notes / next upgrades

- If your org becomes very large, consider a dedicated “closure table” for fast subtree queries.
- Add audit logs (who changed reporting manager, who reset passwords, etc.)
- Add “Departments/Teams” entities if you want additional grouping beyond reporting lines.

---

## Deploy on Railway.app (recommended “no-VPS” option)

### 1) Push this project to GitHub

```bash
git init
git add .
git commit -m "Initial HR Portal"
git branch -M main
# Create a GitHub repo, then:
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2) Create Railway project + add Postgres

1. Railway → **New Project** → **Deploy from GitHub repo**
2. Select your repo
3. Click **Add Service** → **Database** → **PostgreSQL**

### 3) Set environment variables (Railway → Service → Variables)

Set these variables on the **web service**:
- `DJANGO_DEBUG` = `0`
- `DJANGO_SECRET_KEY` = (a long random string)
- `DJANGO_ALLOWED_HOSTS` = `.railway.app`
- `DJANGO_CSRF_TRUSTED_ORIGINS` = `https://*.railway.app`
- `HR_DEFAULT_PASSWORD` = `Welcome@123` (optional)

If your Railway Postgres does **not** provide `DATABASE_URL`, add these mappings:
- `PGDATABASE` = `${{Postgres.PGDATABASE}}`
- `PGUSER` = `${{Postgres.PGUSER}}`
- `PGPASSWORD` = `${{Postgres.PGPASSWORD}}`
- `PGHOST` = `${{Postgres.PGHOST}}`
- `PGPORT` = `${{Postgres.PGPORT}}`

### 4) Configure the start command

Railway → your **web service** → **Settings** → **Start Command**:

```bash
bash start.sh
```

(`start.sh` runs `migrate`, `collectstatic`, then starts Gunicorn on `$PORT`)

### 5) First admin account

After first deploy, open Railway → **web service** → **Shell** and run:

```bash
python manage.py bootstrap_admin --employee-id 1001 --name "HR Admin"
```

Then open your Railway public domain:
- Admin login: `/admin-login/`


