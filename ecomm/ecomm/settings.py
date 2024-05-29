"""
Django settings for ecomm project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https: //docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https: //docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
from decouple import config


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['192.168.1.2','127.0.0.1','172.235.17.58','adarshpbaiju.site','www.adarshpbaiju.site']
SECURE_CROSS_ORIGIN_OPENER_POLICY='same-origin-allow-popups'


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # custom Apps
    'accounts',
    'brand',
    'category',
    'store',
    'carts',
    'orders',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
]

SESSION_EXPIRE_SECONDS = 600

SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

SESSION_TIMEOUT_REDIRECT = 'account/login'

ROOT_URLCONF = "ecomm.urls"

TEMPLATES = [
    {
        "BACKEND" : "django.template.backends.django.DjangoTemplates",
        "DIRS"    : ['templates'],
        "APP_DIRS": True,
        "OPTIONS" : {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ecomm.context_processors.counter",
                "ecomm.context_processors.cart_view",
            ],
        },
    },
]

WSGI_APPLICATION = "ecomm.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config('DB_NAME'),
        'USER':config('DB_USER'),
        'PASSWORD':config( 'DB_PASSWORD') ,
        'HOST': config( 'DB_HOST' ),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR/ "static"

STATICFILES_DIRS =[
    'ecomm/static'
]

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR /'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = 'accounts.Account'


MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.INFO: 'warning',
}

# SMTP Configuration
EMAIL_HOST=config('EMAIL_HOST')
EMAIL_PORT=config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER=config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS=config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL=config('DEFAULT_FROM_EMAIL')


AUTHENTICATION_BACKENDS = [
    'accounts.backends.CustomAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]


TWILIO_ACCOUNT_SID =config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN =config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER =config('TWILIO_PHONE_NUMBER')