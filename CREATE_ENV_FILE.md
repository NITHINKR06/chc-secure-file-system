# Create .env File - Quick Setup

## Step 1: Create .env file

Create a file named `.env` in the project root directory (`E:\5thSem\INS\Project - Copy\.env`)

## Step 2: Copy this content into .env

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
HOST=127.0.0.1
PORT=5000

# Security - Generated SECRET_KEY
SECRET_KEY=87750c2813302775bdbd54c62c468e5db046a40085621df07cb30508cffdc669

# CORS Configuration - Allow all origins for development
ALLOWED_ORIGINS=*

# File Upload Configuration
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO

# Admin Configuration (Optional)
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=your-strong-password-here
```

## Step 3: Save the file

Save the `.env` file in the project root.

## Step 4: Run the application

Now you can run:
```bash
python dev_runner.py
```

## PowerShell Command to Create .env (Alternative)

Run this in PowerShell from the project directory:

```powershell
@"
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
HOST=127.0.0.1
PORT=5000

# Security - Generated SECRET_KEY
SECRET_KEY=87750c2813302775bdbd54c62c468e5db046a40085621df07cb30508cffdc669

# CORS Configuration - Allow all origins for development
ALLOWED_ORIGINS=*

# File Upload Configuration
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
```

---

**Note:** The `.env` file is in `.gitignore` and will not be committed to version control (this is correct for security).

