# 🚀 Diagrams Migration Deployment Guide

## 🚨 **URGENT: Migration Required**

The error you're experiencing is because the `diagrams` column doesn't exist in the production database. Here are **3 ways** to fix this:

## ⚡ **Option 1: Quick Fix via Render Dashboard (Recommended)**

If you have **Shell access** on Render:

1. **Go to your Render service dashboard**
2. **Click on "Shell" tab**
3. **Run the migration command:**
   ```bash
   python manage.py migrate courses 0016
   ```
4. **Verify success:**
   ```bash
   python manage.py showmigrations courses
   ```

## 🛠️ **Option 2: Management Command (If no Shell access)**

Use the custom management command I created:

1. **Deploy the new management command** (already committed)
2. **Add to your startup process:**
   ```bash
   # In your Render build/start command, add:
   python manage.py apply_diagrams_migration
   
   # Or with force flag:
   python manage.py apply_diagrams_migration --force
   ```

## 🔧 **Option 3: Startup Script (Alternative)**

Use the standalone script:

1. **Add to your startup script:**
   ```bash
   # Before starting your Django app:
   python apply_diagrams_migration.py
   ```

2. **Or modify your Procfile:**
   ```
   release: python apply_diagrams_migration.py
   web: gunicorn garaad.wsgi:application
   ```

## 🗃️ **Option 4: Direct SQL (Emergency Fix)**

If all else fails, run this SQL directly in your database:

```sql
-- Connect to your PostgreSQL database and run:
ALTER TABLE courses_problem 
ADD COLUMN diagrams JSONB NULL;

-- Add a comment for documentation:
COMMENT ON COLUMN courses_problem.diagrams IS 'Multiple diagram configurations for complex problems';

-- Insert migration record to prevent re-running:
INSERT INTO django_migrations (app, name, applied) 
VALUES ('courses', '0016_add_diagrams_field', NOW());
```

## 📊 **Current Migration Status**

Your migration file `0016_add_diagrams_field.py` adds:
```sql
ALTER TABLE courses_problem 
ADD COLUMN diagrams JSONB NULL;
```

## 🔍 **Verify Migration Success**

After applying the migration, verify with:

```bash
# Check if column exists:
python manage.py dbshell

# In PostgreSQL prompt:
\d courses_problem

# Look for 'diagrams' column in the output
```

## ⚠️ **Important Notes**

1. **Zero Downtime**: The migration adds a nullable column, so it's safe to apply in production
2. **Backward Compatible**: Existing problems will have `diagrams = NULL`
3. **No Data Loss**: This only adds a new column
4. **Rollback Safe**: Can be rolled back if needed

## 🚀 **Recommended Deployment Steps**

### For Render Free Plan (No Shell):

1. **Deploy the management command:**
   ```bash
   git add .
   git commit -m "Add diagrams migration management command"
   git push origin main
   ```

2. **Update your start command in Render:**
   ```bash
   python manage.py apply_diagrams_migration && python manage.py runserver 0.0.0.0:$PORT
   ```

3. **Or use release phase:**
   Add to `render.yaml`:
   ```yaml
   services:
     - type: web
       name: garaad-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python manage.py runserver 0.0.0.0:$PORT
       preDeployCommand: python manage.py apply_diagrams_migration
   ```

### For Render with Shell Access:

1. **Go to Render dashboard → Your service → Shell**
2. **Run:**
   ```bash
   python manage.py migrate courses 0016
   ```
3. **Verify:**
   ```bash
   python manage.py showmigrations courses
   ```

## 🆘 **If Migration Fails**

If the migration fails, you can manually create the column:

```python
# In Django shell or management command:
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        ALTER TABLE courses_problem 
        ADD COLUMN IF NOT EXISTS diagrams JSONB NULL;
    """)
```

## ✅ **Success Indicators**

You'll know the migration worked when:

1. **No more column errors** when accessing `/api/lms/problems/`
2. **Migration shows as applied:** `[X] 0016_add_diagrams_field`
3. **API responses include diagrams field**

## 📞 **Next Steps After Migration**

1. **Test the API endpoints:**
   - `GET /api/lms/problems/225/` (should work now)
   - `POST /api/lms/problems/` (with both diagram formats)

2. **Monitor logs** for any other issues

3. **Test frontend integration** with multiple diagrams

---

**Choose the option that works best for your Render setup. Option 1 (Shell) is fastest if available, Option 2 (Management Command) is best for automated deployments.** 