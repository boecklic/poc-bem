"""
Django settings for layerservice project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fcgo&yll=@d&&j@79(w3o1c(v%@t&(uie9^i+0#9hsl+&-$nt^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'mptt',                 # tree models in django
    'drf_yasg',             # Yet another swagger generator
    'django_ace',           # ace editor in django admin (DOES NOT WORK YET)
    'prettyjson',           # nice json in admin
    'bod_master.apps.BodMasterConfig',
    'layers.apps.LayersConfig',
    'translation.apps.TranslationConfig',
    'catalog.apps.CatalogConfig',
    'publication.apps.PublicationConfig',
    'geo.apps.GeoConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'layerservice.urls'

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

WSGI_APPLICATION = 'layerservice.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# CREATE USER layerservice WITH PASSWORD 'layerservice';
# We need database with utf8 encoding (for jsonfield) and utf8 needs template0
# CREATE DATABASE dj_layerservice WITH OWNER layerservice ENCODING 'UTF8' TEMPLATE template0;
# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO layerservice;

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dj_layerservice',
        # 'USER': 'postgres',
        # 'PASSWORD': 'yZ_vujnX4QRKakyZ.vph',
        'USER': 'layerservice',
        'PASSWORD': 'layerservice',
        'HOST': 'localhost',
        # 'HOST': 'dj-layerservice.cy0tgrztbs1d.eu-west-1.rds.amazonaws.com',
        'PORT': '5432'
    },
    # default config for legacy data
    're2': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bod_master',
        'USER': 'www-data',
        'PASSWORD': 'www-data',
        'HOST': 'pg-0.dev.bgdi.ch',
        'PORT': '5432'
    },
    # Django doesn't support postgres database schemas out of the box,
    # so we create a separate connection per schema
    # Note: we could use this connection for all legacy models, it's
    # left here as a reference in case of future needs of this functionality
    're3': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=public,re3'
        },
        'NAME': 'bod_master',
        'USER': 'www-data',
        'PASSWORD': 'www-data',
        'HOST': 'pg-0.dev.bgdi.ch',
        'PORT': '5432'
    },
}

# use a custom router to support schemas
DATABASE_ROUTERS = ('layerservice.dbrouter.SchemaEnabledDBRouter',)

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

## Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{levelname} {message}',
            'style': '{'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/ltboc/src/poc-layerservice/layerservice/debug.log',
        },
        'db': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/ltboc/src/poc-layerservice/layerservice/db.log'
        },
        'json': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db'],
            'level': 'DEBUG',
            'propagate': True
        },
        'default': {
            'handlers': ['file', 'json'],
            'level': 'DEBUG',
            'propagate': True
        }
    },
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/layerservice/static/'

STATIC_ROOT = "/home/ltboc/src/poc-layerservice/static/"


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework_yaml.parsers.YAMLParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_yaml.renderers.YAMLRenderer',
    ],
}
