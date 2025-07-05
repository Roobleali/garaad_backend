# Production Migration Fix Guide

## 🚨 **Issue**
Your production database is missing the `referral_code` column that was added in the referral system migration. This is causing a `ProgrammingError: column accounts_user.referral_code does not exist` error.

## 🔧 **Solution Options**

### **Option 1: Apply Migration via Railway Console (Recommended)**

1. **Access Railway Console**
   ```bash
   # Go to your Railway dashboard
   # Navigate to your garaad-backend service
   # Click on "Deployments" tab
   # Find your latest deployment
   # Click "View Logs" or "Console"
   ```

2. **Run Migration Command**
   ```bash
   # In the Railway console, run:
   python manage.py migrate accounts
   ```

3. **Verify Migration**
   ```bash
   # Check if migration was applied
   python manage.py showmigrations accounts
   ```

### **Option 2: Use the Migration Script**

1. **Upload the Script**
   - Upload `apply_production_migration.py` to your Railway deployment
   - Or run it directly in the Railway console

2. **Run the Script**
   ```bash
   python apply_production_migration.py
   ```

### **Option 3: Manual SQL (If Django Migration Fails)**

1. **Connect to Your Database**
   - Get your database connection details from Railway
   - Connect using psql or your preferred database client

2. **Run the SQL Script**
   ```sql
   -- Run the contents of fix_referral_system.sql
   ALTER TABLE accounts_user ADD COLUMN referral_code VARCHAR(8) DEFAULT '';
   ALTER TABLE accounts_user ADD COLUMN referred_by_id INTEGER NULL;
   ALTER TABLE accounts_user ADD COLUMN referral_points INTEGER DEFAULT 0;
   -- ... (rest of the SQL script)
   ```

## 🚀 **Quick Fix Steps**

### **Step 1: Access Railway Console**
1. Go to [Railway Dashboard](https://railway.app)
2. Select your `garaad-backend` project
3. Click on the latest deployment
4. Click "Console" or "Shell"

### **Step 2: Apply Migration**
```bash
# In the Railway console, run:
python manage.py migrate accounts
```

### **Step 3: Verify Fix**
```bash
# Check if the column exists
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"\"\"
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'accounts_user' 
        AND column_name = 'referral_code'
    \"\"\")
    result = cursor.fetchone()
    print('referral_code column exists:', result is not None)
"
```

### **Step 4: Test API**
After applying the migration, test your API endpoint:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-railway-app.railway.app/api/lms/user-progress/
```

## 🔍 **Troubleshooting**

### **If Migration Fails**

1. **Check Database Connection**
   ```bash
   python manage.py dbshell
   # Test connection and run SQL manually
   ```

2. **Manual Column Addition**
   ```sql
   -- Add columns manually if migration fails
   ALTER TABLE accounts_user ADD COLUMN referral_code VARCHAR(8) DEFAULT '';
   ALTER TABLE accounts_user ADD COLUMN referred_by_id INTEGER NULL;
   ALTER TABLE accounts_user ADD COLUMN referral_points INTEGER DEFAULT 0;
   ```

3. **Check for Conflicts**
   ```bash
   # Check if columns already exist
   python manage.py shell -c "
   from django.db import connection
   with connection.cursor() as cursor:
       cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \\'accounts_user\\'')
       columns = [row[0] for row in cursor.fetchall()]
       print('Existing columns:', columns)
   "
   ```

### **If Still Getting Errors**

1. **Restart the Application**
   - In Railway dashboard, restart your deployment
   - This ensures the new schema is loaded

2. **Check Logs**
   ```bash
   # View application logs in Railway
   # Look for any remaining database errors
   ```

3. **Verify Environment Variables**
   - Ensure `DATABASE_URL` is correctly set
   - Check if database connection is working

## 📊 **Verification Commands**

### **Check Migration Status**
```bash
python manage.py showmigrations accounts
```

### **Check Database Schema**
```bash
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \\'accounts_user\\' ORDER BY column_name')
    columns = [row[0] for row in cursor.fetchall()]
    print('User table columns:')
    for col in columns:
        print(f'  - {col}')
"
```

### **Test User Model**
```bash
python manage.py shell -c "
from accounts.models import User
user = User.objects.first()
if user:
    print(f'User: {user.username}')
    print(f'Referral code: {user.referral_code}')
    print(f'Referral points: {user.referral_points}')
else:
    print('No users found')
"
```

## 🎯 **Expected Outcome**

After applying the migration, you should see:
- ✅ No more `ProgrammingError: column accounts_user.referral_code does not exist`
- ✅ API endpoints working normally
- ✅ All users have referral codes
- ✅ Referral system functionality working

## 🔄 **Prevention for Future**

1. **Always test migrations locally first**
2. **Use staging environment for testing**
3. **Backup database before major migrations**
4. **Monitor deployment logs for migration issues**

## 📞 **If You Need Help**

If the migration still fails, you can:
1. Check Railway logs for specific error messages
2. Try the manual SQL approach
3. Contact support with the specific error details

The key is to add the missing `referral_code`, `referred_by_id`, and `referral_points` columns to your production database. 