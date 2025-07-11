"""
Django settings for backend_api project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import dj_database_url
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# Helper for env variables
def env(key: str, default: str | None = None):
    val = os.getenv(key, default)
    if val is None:
        raise ImproperlyConfigured(f"Missing required environment variable: {key}")
    return val

SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "papertigercinema.com",
    "www.papertigercinema.com",
    "paper-tiger-backend.onrender.com",
    "api.papertigercinema.com",
    "genuine-hope.up.railway.app", 
]




# Application definition

INSTALLED_APPS = [
    "jazzmin", 
    'django.contrib.admin',
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'movies',
    #'accounts',
    'accounts.apps.AccountsConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # optional but recommended for refresh token rotation
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django.contrib.staticfiles',
    "django.contrib.sites",          #  ← needed by allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",         # (you can drop this if you won’t use OAuth)
]

MIDDLEWARE = [
    # CORS middleware should be placed as high as possible, especially before
    # other middleware that might generate responses (like CommonMiddleware or CSRF)
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 20,
    'DEFAULT_PAGINATION_CLASS': None,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        # For production, you'd likely want:
        # 'rest_framework.permissions.IsAuthenticated',
        # and then use `@permission_classes([AllowAny])` on specific views like login/register
    ],
}

ROOT_URLCONF = 'backend_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True  # Ensures `?sslmode=require` is respected
    )
}

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

SITE_ID = 1                          # required

# ─── Allauth behaviour ──────────────
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGIN_METHODS = { "username" }   # <- new, modern flag
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3


# optional: nicer errors from allauth
ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'accounts.validators.StrongPasswordValidator',  # <-- Add this line
    },
]

# --- E-mail (dev) ---------------------------------
EMAIL_BACKEND      = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST         = env("EMAIL_HOST", "smtp-relay.brevo.com")
EMAIL_PORT         = int(env("EMAIL_PORT", 587))
EMAIL_USE_TLS      = env("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER    = env("EMAIL_HOST_USER", "8f5aa8001@smtp-brevo.com")
EMAIL_HOST_PASSWORD= env("EMAIL_HOST_PASSWORD")          # no default for secrets
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "Paper Tiger Cinema <noreply@papertigercinema.com>")

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"  # or "http" if you're still local
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Paper Tiger Cinema] "

LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "https://papertigercinema.com/login"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "https://papertigercinema.com/login"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # <- Optional fallback


# settings.py (ONLY the LOGGING part should be updated)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{name} {levelname}: {message}', # Corrected format string
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple', # Use the simple formatter for console
        },
    },
    # By configuring the root logger at INFO level and not disabling propagation
    # for specific loggers, all messages should funnel to the console.
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Set the root logger to INFO to capture everything
    },
    'loggers': {
        # Keep specific loggers if you want very fine-grained control,
        # but for initial debugging, the 'root' logger often suffices.
        # Ensure 'propagate' is not set to False if you want them to bubble up.
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            # 'propagate': False, # Can remove or keep, but root will catch anyway
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            # 'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            # 'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO',
            # 'propagate': False,
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'INFO',
            # 'propagate': False,
        },
        'movies': {
            'handlers': ['console'],
            'level': 'INFO',
            # 'propagate': False,
        },
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# --- CORS Settings ---
# CORS_ALLOW_ALL_ORIGINS = True # <-- Be careful with this in production!
# If CORS_ALLOW_ALL_ORIGINS is True, CORS_ALLOWED_ORIGINS is ignored.
# It's better to list specific origins for security.
CORS_ALLOWED_ORIGINS = [
    "https://papertigercinema.com",
    "https://www.papertigercinema.com",
    "https://api.papertigercinema.com",
]

# If you need to allow credentials (like cookies or auth headers)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",          # ← the missing bit
]

CORS_EXPOSE_HEADERS = ["Authorization"]  

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

CSRF_TRUSTED_ORIGINS = [
    "https://papertigercinema.com",
    "https://www.papertigercinema.com",
    "https://api.papertigercinema.com",
]



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "static"]


STATIC_ROOT = BASE_DIR / "staticfiles"  # for collectstatic

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
