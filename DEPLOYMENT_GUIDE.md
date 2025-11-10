# CHC Secure File Management System - Deployment Guide

This guide covers various hosting options for your CHC Secure File Management System.

## 🏗️ Application Architecture

Your application consists of:
- **Backend**: Flask (Python) API server on port 5000
- **Frontend**: React + Vite + TypeScript on port 5173 (dev) or static build
- **Storage**: Local file system (uploads, encrypted files, metadata)

## 📋 Pre-Deployment Checklist

1. ✅ Test the application locally
2. ✅ Build the frontend: `cd CHCAPP && npm run build`
3. ✅ Ensure all dependencies are in `requirements.txt`
4. ✅ Configure environment variables
5. ✅ Set up persistent storage (for production)

---

## 🌐 Hosting Options

### Option 1: Render (Recommended for Free Tier)

**Pros:**
- Free tier available
- Easy deployment from GitHub
- Automatic SSL certificates
- Supports both backend and frontend

**Steps:**

1. **Prepare for Deployment:**
   ```bash
   # Build frontend
   cd CHCAPP
   npm run build
   cd ..
   ```

2. **Update render.yaml** (already exists):
   ```yaml
   services:
     - type: web
       name: chc-file-management-backend
       env: python
       plan: free
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
       envVars:
         - key: FLASK_ENV
           value: production
         - key: PYTHON_VERSION
           value: 3.11.0
   ```

3. **Deploy Backend:**
   - Push code to GitHub
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect GitHub repository
   - Select `render.yaml` or configure manually
   - Deploy!

4. **Deploy Frontend:**
   - New → Static Site
   - Connect GitHub repository
   - Root Directory: `CHCAPP`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Add environment variable:
     - `VITE_API_URL`: Your backend URL (e.g., `https://chc-file-management-backend.onrender.com`)

5. **Update Frontend API URL:**
   - Edit `CHCAPP/src/utils/api.ts` to use environment variable

**Note:** Free tier spins down after 15 minutes of inactivity. Consider paid tier for production.

---

### Option 2: Railway

**Pros:**
- Simple deployment
- Good free tier ($5 credit/month)
- Automatic deployments
- Persistent storage

**Steps:**

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy Backend:**
   ```bash
   railway init
   railway up
   ```

3. **Configure:**
   - Add environment variables in Railway dashboard
   - Set `PORT` (Railway provides automatically)
   - Set `FLASK_ENV=production`

4. **Deploy Frontend:**
   - Create separate service
   - Build command: `cd CHCAPP && npm install && npm run build`
   - Start command: `cd CHCAPP && npx vite preview --host 0.0.0.0 --port $PORT`

**Cost:** Free tier with $5 credit/month

---

### Option 3: Heroku

**Pros:**
- Well-established platform
- Good documentation
- Add-ons available

**Steps:**

1. **Install Heroku CLI:**
   ```bash
   # Download from heroku.com
   heroku login
   ```

2. **Create Procfile:**
   ```
   web: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

3. **Deploy Backend:**
   ```bash
   heroku create chc-file-management-backend
   git push heroku main
   ```

4. **Deploy Frontend:**
   - Use Heroku static buildpack or deploy separately to Netlify/Vercel

**Cost:** Free tier discontinued, starts at $7/month

---

### Option 4: Vercel (Frontend) + Railway/Render (Backend)

**Pros:**
- Best frontend hosting (Vercel)
- Excellent performance
- Free tier

**Steps:**

1. **Deploy Frontend to Vercel:**
   ```bash
   cd CHCAPP
   npm i -g vercel
   vercel
   ```
   - Set root directory: `CHCAPP`
   - Build command: `npm run build`
   - Output directory: `dist`

2. **Deploy Backend to Railway/Render** (see options above)

3. **Configure:**
   - Add `VITE_API_URL` in Vercel environment variables

**Cost:** Free tier available

---

### Option 5: DigitalOcean App Platform

**Pros:**
- Simple deployment
- Good performance
- Persistent storage support

**Steps:**

1. **Create app.yaml:**
   ```yaml
   name: chc-file-management
   services:
     - name: backend
       github:
         repo: your-username/your-repo
         branch: main
       run_command: gunicorn --bind 0.0.0.0:8080 app:app
       environment_slug: python
       instance_count: 1
       instance_size_slug: basic-xxs
   ```

2. **Deploy:**
   - Connect GitHub in DigitalOcean dashboard
   - Select repository
   - Configure build settings

**Cost:** Starts at $5/month

---

### Option 6: AWS (EC2/Elastic Beanstalk)

**Pros:**
- Highly scalable
- Full control
- Enterprise-grade

**Steps:**

1. **EC2 Instance:**
   ```bash
   # Launch Ubuntu instance
   # SSH into instance
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install -r requirements.txt
   # Configure nginx as reverse proxy
   # Use PM2 or systemd for process management
   ```

2. **Elastic Beanstalk:**
   - Create Python environment
   - Upload application
   - Configure environment variables

**Cost:** Pay-as-you-go (~$10-20/month minimum)

---

### Option 7: Google Cloud Platform (Cloud Run)

**Pros:**
- Serverless
- Pay per use
- Auto-scaling

**Steps:**

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD gunicorn --bind 0.0.0.0:$PORT app:app
   ```

2. **Deploy:**
   ```bash
   gcloud run deploy chc-backend --source .
   ```

**Cost:** Free tier available, then pay-per-use

---

## 🔧 Required Configuration Changes

### 1. Update Frontend API URL

Edit `CHCAPP/src/utils/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
```

### 2. Configure CORS

Your `app.py` already has CORS configured, but ensure it allows your frontend domain:

```python
CORS(app, resources={r"/api/*": {"origins": ["https://your-frontend-domain.com"]}}, supports_credentials=True)
```

### 3. Environment Variables

Create `.env` file or set in hosting platform:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
```

### 4. Persistent Storage

For production, consider:
- **AWS S3** for file storage
- **PostgreSQL** for metadata (instead of JSON files)
- **Redis** for sessions

---

## 📦 Deployment Steps (General)

### Step 1: Build Frontend
```bash
cd CHCAPP
npm install
npm run build
# Output: CHCAPP/dist/
```

### Step 2: Serve Frontend with Backend (Optional)

You can serve the frontend from Flask:

```python
# In app.py
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

### Step 3: Deploy Backend
- Push to GitHub
- Connect to hosting platform
- Configure environment variables
- Deploy!

---

## 🚀 Quick Start: Render Deployment

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy Backend on Render:**
   - Go to render.com
   - New → Web Service
   - Connect GitHub
   - Select repository
   - Use existing `render.yaml` or configure:
     - Build: `pip install -r requirements.txt`
     - Start: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Deploy!

3. **Deploy Frontend on Render:**
   - New → Static Site
   - Connect GitHub
   - Root: `CHCAPP`
   - Build: `npm install && npm run build`
   - Publish: `dist`
   - Add env var: `VITE_API_URL=https://your-backend.onrender.com`

4. **Update API URL in Frontend:**
   - Edit `CHCAPP/src/utils/api.ts` to use `import.meta.env.VITE_API_URL`

---

## ⚠️ Important Notes

1. **File Storage:** Current setup uses local filesystem. For production:
   - Use cloud storage (S3, Google Cloud Storage)
   - Or use persistent volumes on hosting platform

2. **Database:** Currently uses JSON files. For production:
   - Migrate to PostgreSQL, MongoDB, or similar

3. **Security:**
   - Change default admin password
   - Use strong SECRET_KEY
   - Enable HTTPS (most platforms do this automatically)

4. **Scaling:**
   - Current setup is single-instance
   - For multiple instances, use external storage/database

---

## 📝 Recommended Setup for Production

1. **Backend:** Railway or Render (paid tier)
2. **Frontend:** Vercel or Netlify
3. **Storage:** AWS S3 or Google Cloud Storage
4. **Database:** PostgreSQL (Supabase free tier or Railway)
5. **CDN:** Cloudflare (free)

---

## 🆘 Troubleshooting

**Backend won't start:**
- Check PORT environment variable
- Ensure gunicorn is installed
- Check logs in hosting dashboard

**Frontend can't connect to backend:**
- Verify CORS settings
- Check API URL in frontend
- Ensure backend URL is correct

**Files not persisting:**
- Use cloud storage or persistent volumes
- Check file permissions

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

---

**Need help?** Check the hosting platform's documentation or support forums.

