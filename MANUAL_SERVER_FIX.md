# 🚨 IMMEDIATE SERVER FIX - Manual Steps Required

## Problem
1. Git pull in GitHub Actions failed (authentication issue)
2. Server is 14 commits behind
3. GitHub Actions was restarting `gunicorn` instead of `daphne`

## ✅ Fix Applied
Updated `.github/workflows/deploy.yml` to restart `daphne` instead of `gunicorn`.

---

## 🔧 MANUAL FIX (Run These Commands on Server)

SSH into your server and run:

```bash
# 1. Navigate to project
cd /var/www/garaad_backend

# 2. Manually pull latest code (bypass auth issue)
sudo git pull origin main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies (Daphne and Channels)
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Restart Daphne (not gunicorn!)
sudo systemctl restart daphne

# 8. Reload Nginx
sudo systemctl reload nginx

# 9. Check Daphne status
sudo systemctl status daphne

# 10. Watch logs for errors
sudo journalctl -u daphne -f
```

---

## 🎯 What Should Happen

After running these commands:

✅ **Git pull succeeds** (manually with sudo)
✅ **Daphne restarts** with new code
✅ **No more coroutine errors**
✅ **WebSocket connections work**

**Expected in logs:**
```
Started Daphne ASGI application
Listening on Unix socket /var/www/garaad_backend/daphne.sock
WebSocket Auth Success: [username]
User [username] connecting to community_...
```

---

## 🔒 Next Steps

After manual fix works:

### Fix Git Authentication for GitHub Actions

On server, configure git to use SSH instead of HTTPS:

```bash
cd /var/www/garaad_backend
git remote set-url origin git@github.com:Roobleali/garaad_backend.git
```

Then future pushes will trigger GitHub Actions that work properly.

---

## ⚡ Quick Verification

After commands, test WebSocket:
```bash
# Should see Daphne running
sudo systemctl status daphne

# Should show recent connections
sudo journalctl -u daphne -n 50
```

Then refresh your frontend - WebSocket should connect! 🎉
