# Garaad Backend

Django REST API backend for the Garaad learning platform.

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file based on `.env.example`
6. Run migrations: `python manage.py migrate`
7. Run the development server: `python manage.py runserver`

## Deployment

### Prerequisites

- A PostgreSQL database (can use Supabase, Railway, Render, or any other PostgreSQL provider)
- A deployment platform such as Railway, Render, or Heroku

### Deployment to Railway

1. Create a new project on [Railway](https://railway.app/)
2. Link your GitHub repository or use the Railway CLI to push your code
3. Add a PostgreSQL database service
4. Set up the environment variables in the Railway dashboard:
   - `SECRET_KEY`: A secure random string
   - `DEBUG`: Set to `False`
   - `ALLOWED_HOSTS`: Your domain (e.g., `your-app.railway.app`)
   - `CORS_ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://your-frontend-app.vercel.app`)
   - `DATABASE_URL`: This will be automatically set by Railway
5. Deploy the app
6. Run migrations in the Railway terminal: `python manage.py migrate`

### Deployment to Render

1. Create a new Web Service on [Render](https://render.com/)
2. Connect your GitHub repository
3. Configure the service:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn wsgi:application`
4. Add a PostgreSQL database
5. Set environment variables:
   - `SECRET_KEY`: A secure random string
   - `DEBUG`: Set to `False`
   - `ALLOWED_HOSTS`: Your Render domain (e.g., `your-app.onrender.com`)
   - `CORS_ALLOWED_ORIGINS`: Your frontend URL
   - `DATABASE_URL`: This will be automatically set by Render
6. Deploy the app
7. Run migrations in the Render shell: `python manage.py migrate`

### Deployment to Heroku

1. Create a Heroku account and install the Heroku CLI
2. Create a new app: `heroku create your-app-name`
3. Add PostgreSQL addon: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set environment variables:
   ```
   heroku config:set SECRET_KEY=your-secure-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
   heroku config:set CORS_ALLOWED_ORIGINS=https://your-frontend-app.vercel.app
   ```
5. Push code to Heroku: `git push heroku main`
6. Run migrations: `heroku run python manage.py migrate`

## API Documentation

### Auth Endpoints

- `POST /api/auth/signup/`: Create a new user account
- `POST /api/auth/login/`: Log in and get authentication tokens
- `POST /api/auth/refresh/`: Refresh the access token

### User Endpoints

- `GET /api/profile/`: Get user profile
- `POST /api/student/register/`: Register as a student

### Onboarding Endpoints

- `GET /api/onboarding/status/`: Get onboarding status
- `POST /api/onboarding/complete/`: Complete the onboarding process 