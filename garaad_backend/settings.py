DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c statement_timeout=30000',
        },
        'CONN_MAX_AGE': 0,  # Close connections after each request
        'CONN_HEALTH_CHECKS': True,
        'POOL_OPTIONS': {
            'MAX_CONNS': 20,  # Maximum number of connections to keep in the pool
            'TIMEOUT': 30,    # Connection timeout in seconds
        },
        # ... rest of your database settings ...
    }
}

# Add connection pooling middleware
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'garaad_backend.middleware.database.DatabaseConnectionMiddleware',  # Add this line
] 