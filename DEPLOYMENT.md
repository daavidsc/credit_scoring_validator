# Credit Scoring Validator - Deployment Guide

## 🔐 Secure Authentication System

This application now includes enterprise-grade authentication with:
- **bcrypt password hashing** - Military-grade password encryption
- **Flask-Login session management** - Secure user sessions
- **CSRF protection** - Cross-site request forgery prevention
- **Role-based access** - Admin and regular user roles
- **Automatic admin setup** - Default admin account created on first run

## Deploy to Render

This application is configured for easy deployment to Render.com using Gunicorn.

### Quick Deploy

1. **Fork/Clone this repository** to your GitHub account

2. **Connect to Render**:
   - Go to [Render.com](https://render.com)
   - Create a new account or sign in
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository

3. **Configure the deployment**:
   - **Name**: `credit-scoring-validator`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh`
   - **Plan**: Free (or paid for better performance)

4. **Environment Variables** (optional):
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: `your-secure-secret-key-here` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `PORT`: `10000` (automatically set by Render)

5. **Deploy**: Click "Create Web Service"

### 🔑 First Login

After deployment, the app will automatically create a default admin account:

1. **Check deployment logs** for the generated admin credentials
2. **Login immediately** with the provided username and password
3. **Change the password** via the Profile page
4. **Create additional users** via the Admin panel

### Alternative: Manual Configuration

If you prefer manual configuration instead of using `render.yaml`:

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `gunicorn app:app --config gunicorn.conf.py`
3. **Environment**: Python 3.11+

### Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Flask development server
python app.py

# Or run with Gunicorn (production-like)
gunicorn app:app --config gunicorn.conf.py
```

**Note**: On first run, the app will display admin credentials in the console.

### Docker Deployment

Alternatively, you can deploy using Docker:

```bash
# Build the image
docker build -t credit-scoring-validator .

# Run the container
docker run -p 8000:8000 credit-scoring-validator
```

### 🔐 Security Features

- **Password Requirements**: Minimum 8 characters, complexity validation
- **Session Security**: Secure cookies, XSS protection, CSRF tokens
- **Role-Based Access**: Admin users can manage other users
- **Password Hashing**: bcrypt with automatic salt generation
- **Secure Defaults**: Production-ready security headers and settings

### 👥 User Management

**Admin Features:**
- Create new users
- Delete users
- View user statistics
- Access all application features

**Regular Users:**
- Change own password
- Access analysis features
- View personal profile

### Features

- **Automated Scaling**: Gunicorn automatically scales workers based on CPU cores
- **Health Checks**: Built-in health check endpoint at `/health`
- **Error Handling**: Comprehensive error logging and handling
- **File Persistence**: Reports and data are stored in persistent directories
- **Background Processing**: Long-running analyses run in background threads
- **Secure Authentication**: Enterprise-grade user authentication system

### File Structure

```
├── app.py                 # Main Flask application with authentication
├── auth/                  # Authentication module
│   ├── __init__.py       # Module initialization
│   ├── user_manager.py   # User management and password hashing
│   └── forms.py          # Login and user forms with validation
├── templates/
│   ├── login.html        # Secure login page
│   ├── admin_users.html  # User management interface
│   └── admin_create_user.html # User creation form
├── gunicorn.conf.py      # Gunicorn configuration
├── start.sh              # Startup script
├── render.yaml           # Render deployment configuration
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies (including auth libraries)
├── config_prod.py        # Production configuration
└── ...                   # Application modules
```

### Monitoring

- Health check endpoint: `https://your-app.onrender.com/health`
- Login page: `https://your-app.onrender.com/login`
- Admin panel: `https://your-app.onrender.com/admin/users` (admin only)
- Application logs available in Render dashboard
- Performance metrics tracked automatically

### Troubleshooting

1. **Build fails**: Check `requirements.txt` for dependency conflicts
2. **App won't start**: Verify `start.sh` is executable and gunicorn config is valid
3. **Can't login**: Check deployment logs for admin credentials
4. **Authentication errors**: Ensure SECRET_KEY is set properly
5. **Performance issues**: Consider upgrading to a paid Render plan
6. **File permissions**: Ensure directories are created properly in startup script

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port (set automatically by Render) |
| `FLASK_ENV` | development | Flask environment mode |
| `SECRET_KEY` | auto-generated | Flask secret key for sessions and CSRF |

### 🔧 Testing

Run the deployment test script to verify everything is working:

```bash
./test_deployment.sh
```

This will test:
- File existence and permissions
- Gunicorn configuration
- Flask app loading
- Authentication system
- Health endpoints
- Login functionality

### Support

For deployment issues, check:
- [Render Documentation](https://render.com/docs)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- Application logs in Render dashboard

### Security Notes

⚠️ **Important Security Reminders:**
- Change default admin password immediately after first login
- Use strong, unique passwords for all accounts
- Keep your SECRET_KEY secure and unique
- Enable HTTPS in production (Render provides this automatically)
- Regularly update dependencies for security patches
