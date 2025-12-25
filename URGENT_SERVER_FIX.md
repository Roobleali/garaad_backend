# 🚨 URGENT FIX - Server Needs Code Update

## Problem
The server is running **OLD CODE**. You pushed the fixes, but the server hasn't pulled them yet.

## Immediate Fix (Run on Server)

```bash
# 1. SSH into server
ssh root@167.172.108.123

# 2. Navigate to project
cd /var/www/garaad_backend

# 3. Pull latest code
git pull origin main

# 4. Restart Daphne
sudo systemctl restart daphne

# 5. Check logs
sudo journalctl -u daphne -f
```

## What Should Happen

After pulling and restarting, you should see:
```
✅ Daphne starting successfully
✅ No AttributeError
✅ WebSocket connections working
```

## If Still Errors After Pull

The error `'coroutine' object has no attribute 'status_code'` means there's an async view somewhere.

Run this on the server:
```bash
cd /var/www/garaad_backend
grep -r "async def" --include="*.py" . | grep -v "\.git" | grep -v consumers.py | grep -v middleware.py
```

If you see ANY results (other than consumers/middleware), those are the problem files.

---

## Quick Verification

After `git pull`, check that `asgi.py` has this:

```bash
cat garaad/asgi.py
```

Should show:
```python
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(...)
})
```

NOT:
```python
"websocket": JwtAuthMiddleware(...)  # ❌ OLD
```
