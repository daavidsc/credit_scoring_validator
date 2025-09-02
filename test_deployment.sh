#!/bin/bash

echo "🚀 Testing Credit Scoring Validator deployment setup..."

# Test 1: Check if required files exist
echo "📁 Checking required files..."
files=("app.py" "gunicorn.conf.py" "start.sh" "requirements.txt" "render.yaml")
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

# Test 5: Test health endpoint
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

echo ""
echo "🎉 All tests passed! Your app is ready for Render deployment."
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render"
echo "3. Deploy using the provided render.yaml configuration"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
