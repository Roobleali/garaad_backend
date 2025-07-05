# CORS Troubleshooting Guide for Referral Endpoints

## 🚨 **Issue: CORS Error with Referral Endpoints**

**Error Message:**
```
Access to fetch at 'https://api.garaad.org/api/auth/referral-stats/' from origin 'http://localhost:3000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ **Solution Applied**

### **1. Fixed CORS Middleware Order**
The CORS middleware must be at the **top** of the middleware stack:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the top
    'django.middleware.security.SecurityMiddleware',
    # ... other middleware
]
```

### **2. Updated CORS Settings**
Added comprehensive CORS configuration in `garaad/settings.py`:

```python
# CORS settings
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_ALL_ORIGINS = True  # For development
else:
    # Production allowed origins
    CORS_ALLOWED_ORIGINS = [
        'https://garaad.org',
        'https://www.garaad.org',
        'https://api.garaad.org',
        'https://garaad-backend-production.up.railway.app',
        'https://garaad-backend-development.up.railway.app',
        'http://localhost:3000',  # For development testing
        'http://127.0.0.1:3000'   # For development testing
    ]

# Additional CORS settings
CORS_ALLOW_ALL_HEADERS = True
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
```

## 🔧 **Verification Steps**

### **1. Check CORS Settings**
Run this test to verify CORS configuration:

```bash
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'CORS_ALLOWED_ORIGINS: {getattr(settings, \"CORS_ALLOWED_ORIGINS\", [])}')
print(f'CORS_ALLOW_ALL_ORIGINS: {getattr(settings, \"CORS_ALLOW_ALL_ORIGINS\", False)}')
"
```

### **2. Test Referral Endpoints**
Use these curl commands to test the endpoints:

```bash
# Test referral stats endpoint
curl -X GET \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  https://api.garaad.org/api/auth/referral-stats/

# Test referrals endpoint
curl -X GET \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  https://api.garaad.org/api/auth/referrals/
```

### **3. Check Preflight Request**
Test the OPTIONS preflight request:

```bash
curl -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  https://api.garaad.org/api/auth/referral-stats/
```

## 🎯 **Frontend Implementation**

### **1. Proper Headers in Frontend**
Ensure your frontend requests include the correct headers:

```javascript
// Example fetch request
const response = await fetch('https://api.garaad.org/api/auth/referral-stats/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  credentials: 'include', // If using cookies
});
```

### **2. Error Handling**
Add proper error handling for CORS issues:

```javascript
try {
  const response = await fetch('https://api.garaad.org/api/auth/referral-stats/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  console.log('Referral stats:', data);
} catch (error) {
  console.error('CORS or network error:', error);
  // Handle error appropriately
}
```

## 🔍 **Common Issues and Solutions**

### **Issue 1: CORS middleware not at top**
**Solution:** Move `corsheaders.middleware.CorsMiddleware` to the first position in `MIDDLEWARE`.

### **Issue 2: Missing Authorization header**
**Solution:** Add `'authorization'` to `CORS_ALLOW_HEADERS`.

### **Issue 3: Production vs Development**
**Solution:** Ensure both development and production origins are included in `CORS_ALLOWED_ORIGINS`.

### **Issue 4: Preflight request failing**
**Solution:** Ensure `OPTIONS` is included in `CORS_ALLOW_METHODS`.

## 📊 **Environment Variables**

You can also configure CORS via environment variables:

```bash
# Add to your environment
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://anotherdomain.com
```

## 🚀 **Deployment Notes**

### **For Railway/Production:**
1. The CORS settings are now properly configured for production
2. Both `https://api.garaad.org` and `http://localhost:3000` are allowed
3. All necessary headers and methods are configured

### **For Local Development:**
1. `CORS_ALLOW_ALL_ORIGINS = True` when `DEBUG = True`
2. Localhost origins are explicitly allowed in production settings

## ✅ **Expected Response Headers**

After the fix, your API responses should include these headers:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: DELETE,GET,OPTIONS,PATCH,POST,PUT
Access-Control-Allow-Headers: accept,accept-encoding,authorization,content-type,dnt,origin,user-agent,x-csrftoken,x-requested-with
```

## 🔄 **Testing Checklist**

- [ ] CORS middleware is at the top of the stack
- [ ] All required origins are in `CORS_ALLOWED_ORIGINS`
- [ ] `authorization` header is in `CORS_ALLOW_HEADERS`
- [ ] `OPTIONS` method is in `CORS_ALLOW_METHODS`
- [ ] Preflight requests return 200 OK
- [ ] Actual requests include proper Authorization header
- [ ] Frontend handles CORS errors gracefully

## 📞 **If Issues Persist**

1. **Check server logs** for CORS-related errors
2. **Verify the deployment** - ensure changes are live
3. **Test with curl** to isolate frontend vs backend issues
4. **Check browser dev tools** for detailed CORS error messages
5. **Verify JWT token** is valid and properly formatted

The CORS configuration has been updated and deployed. Your referral endpoints should now work properly from both localhost and production environments. 