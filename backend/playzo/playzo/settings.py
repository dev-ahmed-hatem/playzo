# for this project
from datetime import timedelta

import pytz
from corsheaders.defaults import default_headers

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!9n1vr75qowg1fl3j6te@ukrvd^%)y4_m0vd_sed$olka*mt#3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['10.0.2.2', '127.0.0.1', 'localhost', 'playzo.pythonanywhere.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # openapi
    'drf_spectacular',
    'drf_spectacular_sidecar',

    'authentication.apps.AuthenticationConfig',
    'users.apps.UsersConfig',
    'players.apps.PlayersConfig',
    'offers.apps.OffersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'playzo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'playzo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('ar-eg', 'Arabic'),
    ('en-us', 'English'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'UTC'
CAIRO_TZ = pytz.timezone('Africa/Cairo')

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom Settings
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.authentication.BaseAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'playzo.rest_framework_utils.custom_pagination.CustomPageNumberPagination',

    # openapi
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# simple jwt:
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=180),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# corsheaders
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-CSRFToken'
]

# csrf
# CSRF_TRUSTED_ORIGINS = ['http://localhost:5173']
# CSRF_COOKIE_NAME = 'csrftoken'
# CSRF_HEADER_NAME = 'X-CSRFToken'
# CSRF_COOKIE_SAMESITE = 'Lax'
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True


# Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Playzo API Documentation',
    'DESCRIPTION': """
    # Complete API Documentation

    Welcome to the API documentation for the Flutter application.

    ## 🔐 Authentication
    Most endpoints require JWT authentication. Include the token in the header:
    ```
    Authorization: Bearer <your_jwt_token>
    ```

    ## 🌐 Base URL
    ```
    https://playzo.pythonanywhere.com/api/
    ```

    ## 📝 Quick Start
    1. Get your JWT token from authentication endpoints
    2. Use it in the Authorization header
    3. Explore endpoints below

    ## 📊 Rate Limits
    - Public endpoints: 100 requests/hour
    - Authenticated: 1000 requests/hour
    - Admin endpoints: 5000 requests/hour

    ## 🔍 Common Query Parameters
    | Parameter | Description | Example |
    |-----------|-------------|---------|
    | `search` | Full-text search | `?search=futsal` |
    | `ordering` | Sort results | `?ordering=-created_at` |
    | `limit` | Pagination limit | `?limit=10` |
    | `offset` | Pagination offset | `?offset=20` |

    ## 📞 Support
    - Email: kaffo2024@gmail.com
    - Slack: #api-support
    """,
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'tagsSorter': 'alpha',
        'operationsSorter': 'alpha',
    },
    'COMPONENT_SPLIT_REQUEST': True,  # Better request body documentation
    'SCHEMA_PATH_PREFIX': r'/api/',  # API prefix
    'SCHEMA_COERCE_PATH_PK_SUFFIX': True,  # Convert {id} to pk
}
