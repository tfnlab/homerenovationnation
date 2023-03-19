"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

HTTP_TIMEOUT = 1800

APPEND_SLASH = False
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  os.environ.get('D_SECRET_KEY')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('D_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('D_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'prompt': 'consent',
}

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'store.pipeline.get_email',  # Add the custom function here
    'store.pipeline.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'store.pipeline.user_details',
)



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['store.homerenovationnation.com', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://store.homerenovationnation.com']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


X_CSRFTOKEN_HEADER = 'X-CSRFTOKEN'
X_CSRF_TOKEN_HEADER = 'X-CSRF-TOKEN'

# Application definition

SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "https://modernfarms.io/accounts/google/login/callback/"
LOGOUT_REDIRECT_URL = "/"
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "671997132137-5i4r4r1rmr0d5nun850lob7j2j5bv6f4.apps.googleusercontent.com",
            "secret": "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",
            "key": "671997132137-5i4r4r1rmr0d5nun850lob7j2j5bv6f4.apps.googleusercontent.com"
        }
    }
}


INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'social_django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]


AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'social_core.backends.google.GoogleOAuth2',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'website.wsgi.application'


# Database LOCAL MYSQL INSTNCE DEPLOYMENT
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases



## RDS Deployment
# AWS RDS settings
RDS_DATABASE = os.environ.get('RDS_DATABASE')
RDS_USERNAME = os.environ.get('RDS_USERNAME')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
RDS_HOST = os.environ.get('RDS_HOST')
RDS_PORT = os.environ.get('RDS_PORT')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': RDS_DATABASE,
        'USER': RDS_USERNAME,
        'PASSWORD': RDS_PASSWORD,
        'HOST': RDS_HOST,
        'PORT': RDS_PORT,
    }
}

# USED FOR Heroku deployment
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['CLEARDB_DATABASE_NAME'],
        'USER': os.environ['CLEARDB_DATABASE_USER'],
        'PASSWORD': os.environ['CLEARDB_DATABASE_PASSWORD'],
        'HOST': os.environ['CLEARDB_DATABASE_HOST'],
        'PORT': os.environ['CLEARDB_DATABASE_PORT'],
    }
}
'''

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/



STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL="store.User"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/log/file.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
