#!/bin/bash

# Railway Migration Fix Script
# This script should be run on Railway to fix the referral_code column issue

echo "=== Railway Migration Fix ==="
echo "This script will apply the referral system migration to your production database"
echo ""

# Check if we're in Railway environment
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not found. This script should be run on Railway."
    exit 1
fi

echo "✅ DATABASE_URL found"
echo ""

# Apply the migration
echo "Applying accounts migration..."
python manage.py migrate accounts

if [ $? -eq 0 ]; then
    echo "✅ Migration applied successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

echo ""

# Verify the migration
echo "Verifying migration..."
python manage.py showmigrations accounts

echo ""

# Test the User model
echo "Testing User model..."
python manage.py shell -c "
from accounts.models import User
user = User.objects.first()
if user:
    print(f'✅ User model has referral_code: {hasattr(user, \"referral_code\")}')
    print(f'✅ Referral code value: {getattr(user, \"referral_code\", \"NOT_FOUND\")}')
    print(f'✅ Referral points: {getattr(user, \"referral_points\", \"NOT_FOUND\")}')
else:
    print('⚠️  No users found in database')
"

echo ""
echo "=== Migration Complete ==="
echo "Your production database should now have the referral_code column."
echo "Test your API endpoints to verify the fix." 