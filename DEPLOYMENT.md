# DigitalOcean Deployment Guide

Deployment guide for the Garaad Django backend to DigitalOcean App Platform.

**Production URL**: `api.garaad.org` / `167.172.108.123`

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Variables Setup](#environment-variables-setup)
3. [Database Setup](#database-setup)
4. [Static Files](#static-files)
5. [Testing Locally](#testing-locally)
6. [DigitalOcean Configuration](#digitalocean-configuration)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to DigitalOcean, ensure:

- [ ] **Security Review**: No hardcoded secrets in code
- [ ] **Secret Key**: Generated new production `DJANGO_SECRET_KEY`
- [ ] **Debug Mode**: `DEBUG=False` in production environment
- [ ] **Database**: PostgreSQL database provisioned and accessible
- [ ] **Static Files**: `python manage.py collectstatic` runs without errors
- [ ] **Gunicorn**: Server starts successfully with `gunicorn garaad.wsgi:application`
- [ ] **Health Check**: `/health/` endpoint returns 200 OK
- [ ] **Migrations**: All migrations are up to date
- [ ] **Dependencies**: `requirements.txt` is complete and tested

---

## Environment Variables Setup

### Required Variables

Set these in **DigitalOcean App Platform → Settings → Environment Variables**:

```bash
# Critical - Django Core
DJANGO_SECRET_KEY=<generate-new-production-key>
DEBUG=False
DJANGO_SETTINGS_MODULE=garaad.settings
ALLOWED_HOSTS=167.172.108.123,api.garaad.org

# Database - PostgreSQL
DB_NAME=<your_database_name>
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
DB_HOST=<your_database_host>
DB_PORT=5432
```

### Optional Variables

```bash
# CORS & Frontend
CORS_ALLOWED_ORIGINS=https://garaad.org,https://www.garaad.org
FRONTEND_URL=https://garaad.org
SITE_URL=https://api.garaad.org
```

### Generate Production Secret Key

Run locally to generate a new secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**IMPORTANT**: Never reuse development secret keys in production!

---

## Database Setup

### 1. Provision PostgreSQL Database

In DigitalOcean:
- Navigate to **Databases** → **Create Database**
- Choose **PostgreSQL** (version 14 or higher recommended)
- Select appropriate size based on your needs
- Note down the connection credentials

### 2. Configure Database Access

- Add your App Platform to the database's **trusted sources**
- Get the connection details from the database dashboard
- Update environment variables with DB credentials

### 3. Run Migrations

After deployment, SSH into your app or use DigitalOcean console:

```bash
python manage.py migrate
```

---

## Static Files

### WhiteNoise Configuration

Static files are served using **WhiteNoise** (already configured in `settings.py`).

### Collect Static Files

Before deployment, test locally:

```bash
python manage.py collectstatic --noinput
```

This collects all static files to the `staticfiles/` directory.

**Note**: DigitalOcean will run this automatically during build if specified in build commands.

---

## Testing Locally

### 1. Test with Gunicorn

Ensure Gunicorn works before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Test Gunicorn
gunicorn garaad.wsgi:application --bind 0.0.0.0:8000
```

Expected output:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXXXX
```

Press `Ctrl+C` to stop.

### 2. Test Health Endpoint

While Gunicorn is running:

```bash
curl http://localhost:8000/health/
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### 3. Test Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn garaad.wsgi:application

# Check admin CSS loads (visit in browser)
# http://localhost:8000/admin/
```

The admin panel should have proper styling.

---

## DigitalOcean Configuration

### App Platform Setup

1. **Create App**:
   - Go to **App Platform** → **Create App**
   - Connect your GitHub/GitLab repository

2. **Configure Build Settings**:
   ```yaml
   # Build Command
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   
   # Run Command
   gunicorn garaad.wsgi:application --bind 0.0.0.0:$PORT
   ```

3. **Set Environment Variables**:
   - Add all required variables from `.env.production.example`
   - Ensure `DEBUG=False`

4. **Configure Health Check**:
   - **HTTP Path**: `/health/`
   - **HTTP Port**: `8000` (or `$PORT`)

5. **Configure Domain**:
   - Add custom domain: `api.garaad.org`
   - Point DNS A record to: `167.172.108.123`
   - Enable **Force HTTPS**

### Database Component

1. **Add Database Component**:
   - Select **PostgreSQL**
   - DigitalOcean will auto-inject `DATABASE_URL` (optional)

2. **Manual Configuration** (recommended):
   - Use individual environment variables (`DB_NAME`, `DB_USER`, etc.)
   - More control and easier debugging

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://api.garaad.org/health/
```

Expected:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. HTTPS Redirect

```bash
curl -I http://api.garaad.org/health/
```

Should return `301` or `302` redirect to HTTPS.

### 3. API Endpoints

Test your API endpoints:

```bash
# Test registration endpoint
curl -X POST https://api.garaad.org/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### 4. Admin Panel

Visit `https://api.garaad.org/admin/` and verify:
- HTTPS is enforced
- Static files (CSS/JS) load correctly
- You can log in

### 5. CORS Configuration

Test from your frontend domain:

```javascript
// From https://garaad.org
fetch('https://api.garaad.org/api/some-endpoint/')
  .then(response => response.json())
  .then(data => console.log(data));
```

Should work without CORS errors.

---

## Troubleshooting

### Issue: "DisallowedHost" Error

**Symptom**: 400 Bad Request with DisallowedHost error

**Solution**: 
- Verify `ALLOWED_HOSTS` includes your domain
- Check environment variable is set correctly
- Restart the app

### Issue: Static Files Not Loading

**Symptom**: Admin panel has no CSS styling

**Solution**:
```bash
# SSH into app and run
python manage.py collectstatic --noinput

# Verify STATICFILES_STORAGE is set
python manage.py diffsettings | grep STATIC
```

### Issue: Database Connection Failed

**Symptom**: Health check returns "unhealthy" with database error

**Solution**:
- Verify database credentials in environment variables
- Check database is running and accessible
- Verify trusted sources include your app's IP
- Test connection manually:
  ```bash
  psql -h $DB_HOST -U $DB_USER -d $DB_NAME
  ```

### Issue: Gunicorn Workers Crashing

**Symptom**: App keeps restarting or returns 502 errors

**Solution**:
- Check DigitalOcean logs for Python errors
- Verify no heavy imports at module level
- Increase worker timeout if needed:
  ```bash
  gunicorn garaad.wsgi:application --timeout 120
  ```

### Issue: CORS Errors

**Symptom**: Frontend can't access API

**Solution**:
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend domain
- Check for `http` vs `https` mismatch
- Verify `CORS_ALLOW_CREDENTIALS = True` if using auth

### Issue: Secret Key Missing

**Symptom**: "ImproperlyConfigured: The SECRET_KEY setting must not be empty"

**Solution**:
- Generate new secret key (see above)
- Set `DJANGO_SECRET_KEY` environment variable
- Restart the app

---

## Production Monitoring

### Recommended Checks

1. **Health Monitoring**: 
   - Set up uptime monitoring for `/health/` endpoint
   - Tools: UptimeRobot, Pingdom, or DigitalOcean Monitoring

2. **Error Logging**:
   - Configure Sentry or similar error tracking
   - Monitor DigitalOcean app logs regularly

3. **Performance**:
   - Monitor response times
   - Track database query performance
   - Watch memory usage of Gunicorn workers

---

## Deployment Blockers ❌

**NEVER deploy if any of these are true**:

- ❌ `DEBUG=True` in production
- ❌ Using `python manage.py runserver` instead of Gunicorn
- ❌ Secrets hardcoded in source code
- ❌ SQLite database in production
- ❌ Missing `DJANGO_SECRET_KEY` environment variable
- ❌ No health check endpoint
- ❌ Static files not configured

---

## Quick Reference

### Essential Commands

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn garaad.wsgi:application --bind 0.0.0.0:8000

# Test health check
curl http://localhost:8000/health/
```

### Environment Variables Checklist

- [ ] `DJANGO_SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS`
- [ ] `DB_NAME`
- [ ] `DB_USER`
- [ ] `DB_PASSWORD`
- [ ] `DB_HOST`
- [ ] `DB_PORT`

---

## Support

For issues specific to:
- **Django Configuration**: Check `garaad/settings.py`
- **DigitalOcean**: Check App Platform logs and documentation
- **Database**: Check DigitalOcean Database logs
- **Gunicorn**: Check application logs for worker errors

---

**Ready to deploy? Double-check the Pre-Deployment Checklist above!** ✅
