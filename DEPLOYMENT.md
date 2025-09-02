# Credit Scoring Validator - Deployment Guide

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
   - `SECRET_KEY`: `your-secure-secret-key-here`
   - `PORT`: `10000` (automatically set by Render)

5. **Deploy**: Click "Create Web Service"

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

### Docker Deployment

Alternatively, you can deploy using Docker:

```bash
# Build the image
docker build -t credit-scoring-validator .

# Run the container
docker run -p 8000:8000 credit-scoring-validator
```

### Features

- **Automated Scaling**: Gunicorn automatically scales workers based on CPU cores
- **Health Checks**: Built-in health check endpoint at `/health`
- **Error Handling**: Comprehensive error logging and handling
- **File Persistence**: Reports and data are stored in persistent directories
- **Background Processing**: Long-running analyses run in background threads

### File Structure

```
├── app.py                 # Main Flask application
├── gunicorn.conf.py      # Gunicorn configuration
├── start.sh              # Startup script
├── render.yaml           # Render deployment configuration
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── config_prod.py        # Production configuration
└── ...                   # Application modules
```

### Monitoring

- Health check endpoint: `https://your-app.onrender.com/health`
- Application logs available in Render dashboard
- Performance metrics tracked automatically

### Troubleshooting

1. **Build fails**: Check `requirements.txt` for dependency conflicts
2. **App won't start**: Verify `start.sh` is executable and gunicorn config is valid
3. **Performance issues**: Consider upgrading to a paid Render plan
4. **File permissions**: Ensure directories are created properly in startup script

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port (set automatically by Render) |
| `FLASK_ENV` | development | Flask environment mode |
| `SECRET_KEY` | auto-generated | Flask secret key for sessions |

### Support

For deployment issues, check:
- [Render Documentation](https://render.com/docs)
- [Gunicorn Documentation](https://gunicorn.org/)
- Application logs in Render dashboard
