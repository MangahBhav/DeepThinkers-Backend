"""
Django settings for esoteric_minds project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import cloudinary
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'esoteric-minds.onrender.com', 'seal-app-yf2u7.ondigitalocean.app', 'localhost']

# Application definition

CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'cloudinary',
    'rest_framework',
    "django_apscheduler",
    'users',
    'posts',
    'ads',
    "channels",
    "chats"
]

INSTALLED_APPS += ('corsheaders',)

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ipinfo_django.middleware.IPinfoMiddleware',
]

ROOT_URLCONF = 'esoteric_minds.urls'

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

WSGI_APPLICATION = 'esoteric_minds.wsgi.application'
ASGI_APPLICATION = 'esoteric_minds.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if os.environ.get('DJANGO_ENV') != "production":
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'esoteric_minds',
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'esoteric_minds',
            'ENFORCE_SCHEMA': False,
            "CLIENT": {
                'name': 'esoteric_minds',
                'host': os.environ.get('MONGO_URI'),
                'username': 'Kcee',
                "password": os.environ.get('MONGO_PASSWORD', ''),
                "authMechanism": "SCRAM-SHA-1"
            }
        }
    }

SPECTACULAR_SETTINGS = {
    # OTHER SETTINGS

    'TITLE': 'Esoteric Minds API',
    'DESCRIPTION': "API documentation for Esoteric minds. "
                   "Esoteric minds is a social media platform for people who are interested in the esoteric.",
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,

    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.auth.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "esoteric_minds.pagination.DefaultNoPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

JWT_ENCRYPTION_METHOD = 'HS256'

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

from djongo.operations import DatabaseOperations

DatabaseOperations.conditional_expression_supported_in_where_clause = (
    lambda *args, **kwargs: False
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra lookup directories for collect static to find static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

#  Add configuration for static files storage using whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

IPINFO_TOKEN = os.environ.get("IPINFO_TOKEN")
IPINFO_FILTER = lambda request: (os.environ.get('DJANGO_ENV') != "production")

EMAIL_BACKEND = 'django_mailgun_mime.backends.MailgunMIMEBackend'
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_DOMAIN_NAME = 'info.kofyimages.com'
DEFAULT_FROM_EMAIL = 'kofy@info.kofyimages.com'

# TASK SCHEDULER
# SCHEDULER_CONFIG = {
#     "apscheduler.jobstores.default": {
#         "class": "django_apscheduler.jobstores:DjangoJobStore"
#     },
#     'apscheduler.executors.processpool': {
#         "type": "threadpool"
#     },
# }
# SCHEDULER_AUTOSTART = True
