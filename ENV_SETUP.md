# Environment Variables Setup Guide

## Quick Start

1. **Copy the example file:**
   ```bash
   # Create .env file from template
   # Note: .env.example is in .gitignore, so create it manually
   ```

2. **Create `.env` file** in the project root with the following content:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
HOST=127.0.0.1
PORT=5000

# Security - REQUIRED FOR PRODUCTION
# Generate a strong secret key: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here-minimum-32-characters-long

# CORS Configuration
# For production, set to your frontend domain(s), comma-separated
# Example: ALLOWED_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
# For development, you can use * (not recommended for production)
ALLOWED_ORIGINS=*

# File Upload Configuration
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO

# Admin Configuration (Optional - for custom admin credentials)
# If not set, default admin (admin/admin123) will be created
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=change-this-strong-password

# Firebase Configuration (Optional - if using Firebase)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-service-account.json

# Rate Limiting Storage (Optional - for production with Redis)
# RATELIMIT_STORAGE_URI=redis://localhost:6379
```

## Required Environment Variables for Production

### 1. SECRET_KEY (REQUIRED)
Generate a strong secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or use:
```bash
openssl rand -hex 32
```

**IMPORTANT:** Never commit your SECRET_KEY to version control!

### 2. FLASK_ENV
Set to `production` for production deployment:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

### 3. ALLOWED_ORIGINS (REQUIRED for Production)
Set to your frontend domain(s):
```bash
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

## Development Setup

For local development, you can use:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
ALLOWED_ORIGINS=*
SECRET_KEY=dev-secret-key-change-in-production
```

## Production Setup

For production deployment:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
ALLOWED_ORIGINS=https://your-frontend.com
SECRET_KEY=<generate-strong-key>
ADMIN_PASSWORD=<strong-password>
```

## Setting Environment Variables

### Local Development
Create a `.env` file in the project root (already in .gitignore)

### Production Deployment

#### Render
1. Go to your service dashboard
2. Navigate to "Environment" tab
3. Add environment variables

#### Railway
1. Go to your service dashboard
2. Navigate to "Variables" tab
3. Add environment variables

#### Heroku
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
heroku config:set ALLOWED_ORIGINS=https://your-frontend.com
```

#### Docker
Add to `docker-compose.yml`:
```yaml
environment:
  - SECRET_KEY=your-secret-key
  - FLASK_ENV=production
  - ALLOWED_ORIGINS=https://your-frontend.com
```

## Security Best Practices

1. ✅ Never commit `.env` file to version control
2. ✅ Use strong, random SECRET_KEY (minimum 32 characters)
3. ✅ Restrict CORS to specific domains in production
4. ✅ Change default admin password
5. ✅ Use different credentials for dev and production
6. ✅ Rotate SECRET_KEY periodically
7. ✅ Use environment variables for all sensitive data

## Troubleshooting

**Error: SECRET_KEY not set**
- Make sure `.env` file exists in project root
- Check that `SECRET_KEY` is set in environment variables
- For production, ensure environment variables are set in hosting platform

**CORS errors**
- Check `ALLOWED_ORIGINS` includes your frontend domain
- Ensure no trailing slashes in URLs
- Check that frontend is using correct API URL

**Rate limiting too strict**
- Adjust limits in `app.py`:
  ```python
  @limiter.limit("10 per minute")  # Increase limit
  ```

