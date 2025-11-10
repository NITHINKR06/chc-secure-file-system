# Troubleshooting Guide

## ✅ Fixed: 500 Error on /api/files

### Issue
The `/api/files` endpoint was returning a 500 Internal Server Error.

### Cause
The endpoint lacked proper error handling, so any exception (like Firestore connection issues or missing metadata) would cause a 500 error.

### Fix Applied
1. ✅ Added comprehensive error handling with try-except blocks
2. ✅ Added fallback to blockchain data if Firestore metadata is unavailable
3. ✅ Added proper logging to identify errors
4. ✅ Added graceful error responses

### What Changed
- The endpoint now catches exceptions at multiple levels
- If Firestore metadata retrieval fails, it falls back to blockchain data
- Errors are logged to `app.log` for debugging
- Returns proper error responses instead of crashing

## 🔍 Debugging Steps

### 1. Check Server Logs
```bash
# View the last 50 lines of the log file
Get-Content app.log -Tail 50

# Or on Linux/Mac:
tail -50 app.log
```

### 2. Check if Backend is Running
```bash
# Test the ping endpoint
curl http://127.0.0.1:5000/api/ping

# Should return: {"status": "ok", "service": "flask", "ts": ...}
```

### 3. Check Firestore Connection
The error might be related to Firestore connection. Check:
- Is Firebase properly configured?
- Is `firebase-service-account.json` in the correct location?
- Is the `GOOGLE_APPLICATION_CREDENTIALS` environment variable set?

### 4. Test the Endpoint Directly
```bash
# Test the files endpoint
curl http://127.0.0.1:5000/api/files

# Check the response and error message
```

## 🐛 Common Issues

### Issue 1: Firestore Connection Error
**Symptoms:** 500 error, log shows Firestore connection issues

**Solution:**
1. Check Firebase credentials
2. Verify `firebase-service-account.json` exists
3. Check environment variables
4. The endpoint now falls back to blockchain data if Firestore fails

### Issue 2: No Files Returned
**Symptoms:** Endpoint returns empty array `[]`

**Solution:**
- This is normal if no files have been uploaded
- Upload a file first to test
- Check blockchain.json to see if files exist

### Issue 3: CORS Errors
**Symptoms:** Browser console shows CORS errors

**Solution:**
1. Check `ALLOWED_ORIGINS` in `.env` file
2. For development, use `ALLOWED_ORIGINS=*`
3. For production, set to your frontend domain

### Issue 4: Rate Limiting
**Symptoms:** 429 Too Many Requests error

**Solution:**
- Rate limiting is now exempted for `/api/files`
- If you see rate limit errors on other endpoints, adjust limits in `app.py`

## 🔧 Testing the Fix

### 1. Restart the Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
python dev_runner.py
```

### 2. Check the Logs
```bash
# Watch the log file for errors
Get-Content app.log -Wait -Tail 20
```

### 3. Test the Endpoint
1. Open browser: http://localhost:5173
2. Login with admin/admin123
3. Navigate to Files page
4. Check browser console for errors
5. Check server logs for detailed error messages

## 📊 Error Response Format

The endpoint now returns proper error responses:

**Success:**
```json
[
  {
    "file_id": "file_...",
    "original_filename": "test.txt",
    "owner": "admin",
    "authorized_users": [],
    "block_hash": "...",
    "timestamp": 1234567890,
    "size": 1024,
    "encrypted_size": 1024
  }
]
```

**Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve files",
  "message": "Error details here"
}
```

## 🚀 Next Steps

1. **Restart the server** to apply the fixes
2. **Check the logs** if errors persist
3. **Test the endpoint** in the browser
4. **Report any new errors** with log details

## 📝 Logging

Errors are now logged to:
- **Console:** Standard output
- **File:** `app.log` in project root
- **Level:** INFO for development, WARNING for production

To change log level, set `LOG_LEVEL` in `.env`:
```bash
LOG_LEVEL=DEBUG  # For detailed debugging
LOG_LEVEL=INFO   # For normal operation
LOG_LEVEL=WARNING  # For production
```

## 🆘 Still Having Issues?

If you're still seeing errors:

1. **Check the log file:** `app.log`
2. **Check browser console:** F12 → Console tab
3. **Check network tab:** F12 → Network tab → Look for `/api/files` request
4. **Verify backend is running:** Check http://127.0.0.1:5000/api/ping
5. **Check environment variables:** Verify `.env` file is correct

## 📚 Related Documentation

- `ENV_SETUP.md` - Environment variables setup
- `SECURITY_FIXES_SUMMARY.md` - Security fixes applied
- `QUICK_START.md` - Quick start guide
- `PRODUCTION_READINESS.md` - Production checklist

---

**The 500 error should now be fixed!** Restart your server and try again.

