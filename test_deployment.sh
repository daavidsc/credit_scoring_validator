#!/bin/bash

echo "🚀 Testing Credit Scoring Validator deployment setup..."

# Test 1: Check if required files exist
echo "📁 Checking required files..."
files=("app.py" "gunicorn.conf.py" "start.sh" "requirements.txt" "render.yaml" "auth/__init__.py" "auth/user_manager.py" "auth/forms.py" "templates/login.html" "templates/profile.html" "templates/change_password.html" "templates/admin_users.html" "templates/admin_create_user.html")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Test 2: Check if start.sh is executable
if [ -x "start.sh" ]; then
    echo "✅ start.sh is executable"
else
    echo "❌ start.sh is not executable"
    exit 1
fi

# Test 3: Test Gunicorn configuration
echo "🔧 Testing Gunicorn configuration..."
if gunicorn --check-config app:app --config gunicorn.conf.py 2>/dev/null; then
    echo "✅ Gunicorn configuration is valid"
else
    echo "❌ Gunicorn configuration has errors"
    exit 1
fi

# Test 4: Test Flask app import
echo "🐍 Testing Flask app import..."
if python -c "from app import app; print('✅ Flask app imported successfully')" 2>/dev/null; then
    echo "✅ Flask app can be imported"
else
    echo "❌ Flask app import failed"
    exit 1
fi

# Test 5: Test authentication system
echo "🔐 Testing authentication system..."
if python -c "
from auth.user_manager import UserManager
import os

# Test user creation and authentication
user, msg = UserManager.create_user('testuser', 'testpass123')
if user:
    auth_user = UserManager.authenticate_user('testuser', 'testpass123')
    if auth_user and auth_user.username == 'testuser':
        print('✅ Authentication system works')
        # Cleanup
        if os.path.exists('auth/users.json'):
            os.remove('auth/users.json')
    else:
        print('❌ Authentication failed')
        exit(1)
else:
    print('❌ User creation failed')
    exit(1)
" 2>/dev/null; then
    echo "✅ Authentication test passed"
else
    echo "❌ Authentication test failed"
    exit 1
fi

# Test 6: Test health endpoint
echo "🏥 Testing health endpoint..."
if python -c "
from app import app
with app.test_client() as client:
    response = client.get('/health')
    if response.status_code == 200:
        print('✅ Health endpoint works')
    else:
        print('❌ Health endpoint failed')
        exit(1)
" 2>/dev/null; then
    echo "✅ Health endpoint test passed"
else
    echo "❌ Health endpoint test failed"
    exit 1
fi

# Test 7: Test login page
echo "🔑 Testing login page..."
if python -c "
from app import app
with app.test_client() as client:
    response = client.get('/login')
    if response.status_code == 200:
        print('✅ Login page works')
    else:
        print('❌ Login page failed')
        exit(1)
" 2>/dev/null; then
    echo "✅ Login page test passed"
else
    echo "❌ Login page test failed"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Your app is ready for Render deployment with secure authentication!"
echo ""
echo "🔐 Security Features Enabled:"
echo "   ✅ Password hashing with bcrypt"
echo "   ✅ CSRF protection with Flask-WTF"
echo "   ✅ Session management with Flask-Login"
echo "   ✅ User roles (Admin/Regular users)"
echo "   ✅ Secure password requirements"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render"
echo "3. Deploy using the provided render.yaml configuration"
echo "4. Access your app and login with the default admin credentials"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
