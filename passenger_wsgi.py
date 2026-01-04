import os
import sys

# ========================================
# IMPORTANT: Update these paths with your actual Hostinger paths
# ========================================
#
# Find your username by logging into Hostinger SSH and running: pwd
# It will show something like: /home/u123456789
# Use that path below
#
# Example paths (REPLACE WITH YOUR ACTUAL PATHS):
# project_home = '/home/u123456789/domains/yourdomain.com/public_html'
# activate_env = '/home/u123456789/python-env/bin/activate_this.py'
#
project_home = '/home/YOUR_USERNAME/domains/YOUR_DOMAIN.com/public_html'
virtualenv_path = '/home/YOUR_USERNAME/python-env'

# Add project to system path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'hr_portal.settings'

# Activate virtual environment
activate_this = os.path.join(virtualenv_path, 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
