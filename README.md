# Garaad Backend

Django REST API backend for the Garaad learning platform.

## Project Overview

This backend provides a comprehensive API for the Garaad learning platform, including:

- User authentication and authorization with JWT
- User profile management and onboarding
- A complete Learning Management System (LMS) with interactive content
- RESTful API endpoints for all functionalities

## Documentation & Resources

- [API Documentation](./API_DOCUMENTATION.md) - Comprehensive documentation of all available endpoints
- [Postman Collection](./garaad_api_postman_collection.json) - Ready-to-use collection for API testing
- [Docker Guide](./DOCKER.md) - Detailed instructions for Docker setup and deployment

## Email Verification

The system includes a robust email verification system using Resend API. This helps prevent fraud and ensures that users provide valid email addresses.

### Quick Start

1. Set up environment variables:
   ```env
   RESEND_API_KEY=your_resend_api_key
   FROM_EMAIL=onboarding@resend.dev  # For development
   RESEND_TEST_MODE=True  # Set to False in production
   ```

2. For detailed documentation, see [EMAIL_VERIFICATION.md](EMAIL_VERIFICATION.md)

### Key Features

- Email verification on signup
- Resend verification email option
- 24-hour code expiration
- One-time use verification codes
- Rate limiting for security
- Comprehensive error handling
- Detailed logging

### Production Setup

For production deployment:
1. Get a production API key from [Resend Dashboard](https://resend.com/api-keys)
2. Verify your domain at [Resend Domains](https://resend.com/domains)
3. Update environment variables with production values

For more details, refer to the [Email Verification Documentation](EMAIL_VERIFICATION.md).

## Quick Start

### Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file based on [.env.example](./.env.example)
6. Run migrations: `python manage.py migrate`
7. Run the development server: `python manage.py runserver`

### Docker Setup

The application can be easily run using Docker:

1. Make sure Docker and Docker Compose are installed on your system
2. Create a `.env` file from the provided [.env.docker](./.env.docker) template:
   ```
   cp .env.docker .env
   ```
3. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```
4. The application will be available at http://localhost:8000

## Deployment Options

### Using Docker (Recommended)

You can deploy the application to any server or cloud provider that supports Docker:

1. Configure your production environment variables in a `.env` file
2. Deploy using Docker Compose:
   ```
   docker-compose -f docker-compose.yml up -d
   ```
3. For production environments, consider using:
   - A reverse proxy like Nginx for SSL termination
   - Container orchestration with Docker Swarm or Kubernetes
   - Automated CI/CD pipelines

### Cloud Platform Options

The application can also be deployed to various cloud platforms:

#### Railway
1. Create a new project on [Railway](https://railway.app/)
2. Link your GitHub repository
3. Add a PostgreSQL database service
4. Configure environment variables
5. Deploy and run migrations

#### Render
1. Create a new Web Service on [Render](https://render.com/)
2. Connect your GitHub repository
3. Configure environment and build settings
4. Add a PostgreSQL database
5. Set environment variables and deploy

#### Heroku
1. Create a new Heroku app
2. Add PostgreSQL addon
3. Configure environment variables
4. Deploy and run migrations

## Using the API

1. Refer to the [API Documentation](./API_DOCUMENTATION.md) for detailed endpoint information
2. Import the [Postman Collection](./garaad_api_postman_collection.json) for easy testing
3. Authenticate using JWT tokens
4. Access the various LMS endpoints to interact with courses, lessons, and interactive content 