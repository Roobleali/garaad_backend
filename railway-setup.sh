#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $DATABASE_URL -p 5432 -q -U postgres; do
  sleep 1
done

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Setup completed successfully!" 