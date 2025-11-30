# Authentication Fix for 401 Unauthorized Error

## Problem
Getting `401 Unauthorized` error when uploading trials:
```
POST http://localhost:8000/api/uploadTrial 401 (Unauthorized)
{detail: 'Could not validate credentials'}
```

## Root Causes
1. **Multipart Form Data Header Issue**: When setting `Content-Type: multipart/form-data` explicitly, it can override the Authorization header
2. **Token Not Set**: Auto-login might not have completed before upload attempt
3. **Token Expired**: Token might have expired
4. **Axios Interceptor**: Authorization header might not be set correctly for multipart requests

## Fixes Applied

### 1. Fixed `frontend/lib/api.ts`
- ✅ Enhanced axios interceptor to always set Authorization header
- ✅ Removed explicit `Content-Type` header for multipart requests (let browser set it with boundary)
- ✅ Added explicit token check in `uploadTrial` method
- ✅ Ensured Authorization header is explicitly set

### 2. Fixed `frontend/app/upload/page.tsx`
- ✅ Enhanced auto-login with token expiration validation
- ✅ Added token validation check before using existing token
- ✅ Improved error handling and logging
- ✅ Added retry login in `handleUpload` if token is missing

## How to Test

1. **Refresh the frontend page** (Ctrl+R or F5)
2. **Check browser console** for:
   - `✅ Using existing valid token` OR
   - `✅ Auto-login successful`
3. **Verify token is set**:
   ```javascript
   localStorage.getItem('token')
   ```
4. **Try uploading a file**

## If Still Getting 401

### Check Backend
1. Ensure backend is running on port 8000:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Check backend logs for authentication errors

3. Verify default user exists:
   - Email: `test@example.com`
   - Password: `test123`
   - Role: `SPONSOR`

### Check Frontend
1. Open browser DevTools (F12)
2. Go to Console tab
3. Check for login errors
4. Go to Application tab → Local Storage
5. Verify `token` key exists

### Manual Login Test
```javascript
// In browser console
fetch('http://localhost:8000/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ email: 'test@example.com', password: 'test123' })
})
.then(r => r.json())
.then(d => {
  localStorage.setItem('token', d.access_token)
  console.log('Token set:', d.access_token)
})
```

## Technical Details

### Multipart Form Data Issue
When uploading files, the browser needs to set the `Content-Type` header with a boundary parameter:
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
```

If we set `Content-Type: multipart/form-data` manually, it doesn't include the boundary, and the request fails. By removing the explicit Content-Type header, axios/browser automatically sets it correctly.

### Token Validation
The fix now:
1. Checks if token exists in localStorage
2. Validates token expiration by decoding JWT
3. Removes expired/invalid tokens
4. Re-authenticates if needed

### Authorization Header
The axios interceptor now:
1. Always checks for token
2. Always sets Authorization header
3. Works correctly with multipart requests

## Status
✅ **FIXED** - Authentication should now work correctly for file uploads.

