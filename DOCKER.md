# Docker Setup for Garaad Backend

This document provides instructions for running the Garaad Backend application using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

## Getting Started

1. Clone the repository:
   ```
   git clone <repository-url>
   cd garaad_backend
   ```

2. Create a `.env` file from the provided `.env.docker` template:
   ```
   cp .env.docker .env
   ```
   
   Note: Make sure to modify the SECRET_KEY in the .env file for production environments.

3. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

   This will start two containers:
   - Web container for the Django application
   - PostgreSQL database container

4. The application will be available at http://localhost:8000

## Dependencies

The Docker setup includes all necessary dependencies, including:

- Python 3.11 and required Python packages
- PostgreSQL 13 database
- Pillow for image handling (used for user profile pictures)
- System dependencies required for these packages

## Additional Commands

### Run Django management commands
```
docker-compose exec web python manage.py <command>
```

Examples:
- Create a superuser: `docker-compose exec web python manage.py createsuperuser`
- Make migrations: `docker-compose exec web python manage.py makemigrations`
- Apply migrations: `docker-compose exec web python manage.py migrate`

### View logs
```
docker-compose logs
```

### Stop the containers
```
docker-compose down
```

### Remove volumes (will delete database data)
```
docker-compose down -v
```

## Troubleshooting

### Image-related errors
If you encounter errors related to image processing, ensure that the container has been built with the necessary system dependencies for Pillow. This should be handled automatically by the Dockerfile, but if issues persist, you may need to install additional system packages.

## Production Deployment

For production deployments:

1. Update the `.env` file with appropriate production values:
   - Set a strong SECRET_KEY
   - Update ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS with your domain
   - Configure any other environment-specific settings

2. Consider using Docker Swarm or Kubernetes for orchestration in production environments.

3. Set up proper SSL termination using a reverse proxy like Nginx.

## Database Backups

To backup the PostgreSQL database:
```
docker-compose exec db pg_dump -U postgres garaad_db > backup.sql
```

To restore from a backup:
```
cat backup.sql | docker-compose exec -T db psql -U postgres -d garaad_db
``` 