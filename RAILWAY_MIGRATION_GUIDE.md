# Railway Migration Guide - Fix Referral System

## 🚨 **The Problem**
Your production database is missing the `referral_code` column, causing this error:
```
ProgrammingError: column accounts_user.referral_code does not exist
```

## 🚀 **Solution: Apply Migration on Railway**

### **Step 1: Access Railway Console**

1. Go to [Railway Dashboard](https://railway.app)
2. Select your `garaad-backend` project
3. Click on the latest deployment
4. Click **"Console"** or **"Shell"**

### **Step 2: Run Migration Command**

In the Railway console, run this command:
```bash
python manage.py migrate accounts
```

### **Step 3: Verify the Fix**

After the migration completes, run these verification commands:

```bash
# Check migration status
python manage.py showmigrations accounts

# Test User model
python manage.py shell -c "
from accounts.models import User
user = User.objects.first()
if user:
    print(f'User model has referral_code: {hasattr(user, \"referral_code\")}')
    print(f'Referral code value: {getattr(user, \"referral_code\", \"NOT_FOUND\")}')
    print(f'Referral points: {getattr(user, \"referral_points\", \"NOT_FOUND\")}')
else:
    print('No users found in database')
"
```

### **Step 4: Test API Endpoint**

After applying the migration, test your API:
```bash
# Test the endpoint that was failing
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-railway-app.railway.app/api/lms/user-progress/
```

## 🔧 **Alternative: Use the Script**

If you prefer, you can also run the provided script:

```bash
# Make the script executable
chmod +x railway_migration_fix.sh

# Run the script
./railway_migration_fix.sh
```

## 📊 **Expected Output**

After successful migration, you should see:
```
Operations to perform:
  Apply all migrations: accounts
Running migrations:
  Applying accounts.0005_user_referral_code_user_referral_points_and_more... OK

accounts
 [X] 0001_initial
 [X] 0002_user_is_email_verified_emailverification
 [X] 0003_studentprofile_daily_goal_minutes_and_more
 [X] 0004_user_subscription_end_date_and_more
 [X] 0005_user_referral_code_user_referral_points_and_more

User model has referral_code: True
Referral code value: [some_code]
Referral points: 0
```

## 🎯 **What This Fixes**

The migration will add these columns to your production database:
- ✅ `referral_code` - Unique 8-character referral codes
- ✅ `referred_by_id` - Foreign key to track who referred each user
- ✅ `referral_points` - Points earned from referrals

## 🔍 **Troubleshooting**

### **If Migration Fails**

1. **Check Database Connection**
   ```bash
   python manage.py dbshell
   ```

2. **Manual SQL Fix**
   ```sql
   -- Add columns manually
   ALTER TABLE accounts_user ADD COLUMN referral_code VARCHAR(8) DEFAULT '';
   ALTER TABLE accounts_user ADD COLUMN referred_by_id INTEGER NULL;
   ALTER TABLE accounts_user ADD COLUMN referral_points INTEGER DEFAULT 0;
   ```

3. **Check for Conflicts**
   ```bash
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
   - View application logs in Railway
   - Look for any remaining database errors

## ✅ **Success Indicators**

After applying the migration, you should see:
- ✅ No more `ProgrammingError: column accounts_user.referral_code does not exist`
- ✅ API endpoints working normally
- ✅ All users have referral codes
- ✅ Referral system functionality working

## 🚀 **Next Steps**

1. **Test your application** to ensure all endpoints work
2. **Monitor logs** for any remaining issues
3. **Verify referral system** functionality if you're using it

The key is to run `python manage.py migrate accounts` in your Railway console to apply the missing migration to your production database. 