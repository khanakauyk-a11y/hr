#!/bin/bash

# HR Portal - Automated Hostinger Setup Script
# This script will automatically set up your HR Portal after uploading to Hostinger

echo "========================================="
echo "HR Portal - Automated Setup"
echo "========================================="
echo ""

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect username and paths automatically
USERNAME=$(whoami)
HOME_DIR=$(eval echo ~$USERNAME)
DOMAIN_PATH=$(pwd)

echo "Detected Configuration:"
echo "  Username: $USERNAME"
echo "  Home Directory: $HOME_DIR"
echo "  Project Path: $DOMAIN_PATH"
echo ""

# Step 1: Create virtual environment
echo "[Step 1/7] Creating Python virtual environment..."
if [ ! -d "$HOME_DIR/python-env" ]; then
    python3 -m venv "$HOME_DIR/python-env"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Step 2: Activate virtual environment and install dependencies
echo "[Step 2/7] Installing dependencies..."
source "$HOME_DIR/python-env/bin/activate"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Step 3: Update passenger_wsgi.py with correct paths
echo "[Step 3/7] Configuring WSGI application..."
sed -i "s|YOUR_USERNAME|$USERNAME|g" passenger_wsgi.py
sed -i "s|YOUR_DOMAIN\.com|$(basename $DOMAIN_PATH)|g" passenger_wsgi.py
echo "✓ WSGI configured"

# Step 4: Update .htaccess with correct paths
echo "[Step 4/7] Configuring Apache..."
if [ -f ".htaccess" ]; then
    sed -i "s|YOUR_USERNAME|$USERNAME|g" .htaccess
    sed -i "s|YOUR_DOMAIN\.com|$(basename $DOMAIN_PATH)|g" .htaccess
    echo "✓ Apache configured"
fi

# Step 5: Create media directory
echo "[Step 5/7] Creating media directories..."
mkdir -p media/offer_letters
chmod 755 media
chmod 755 media/offer_letters
echo "✓ Media directories created"

# Step 6: Run database migrations
echo "[Step 6/7] Setting up database..."
python manage.py migrate --noinput
echo "✓ Database migrated"

# Step 7: Collect static files
echo "[Step 7/7] Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

echo ""
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Create admin user (if needed):"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Restart your application:"
echo "   touch tmp/restart.txt"
echo ""
echo "3. Your site should now be accessible at your domain!"
echo ""
echo "Default Login Credentials:"
echo "  Employee ID: 1001"
echo "  Password: Welcome@123"
echo ""
echo "Configuration Details:"
echo "  Python Path: $HOME_DIR/python-env/bin/python3"
echo "  Project Root: $DOMAIN_PATH"
echo "  WSGI File: $DOMAIN_PATH/passenger_wsgi.py"
echo ""
echo "========================================="
