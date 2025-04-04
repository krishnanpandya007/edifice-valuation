"""
Django settings for valuation_site project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5%ue7)0&=5d%q5(b1$r3=)ff21=axftm$$_)0rj$-r$^6zn6m$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

CORS_ORIGIN_ALLOW_ALL = True # <-------- this
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",    # React (FrontEnd Url) # <-------- this
    "http://192.168.73.153:8000",
    "https://20b0-2409-40c1-3002-3772-287f-3bd6-8ce2-d8bb.ngrok-free.app"
]
CORS_ALLOW_HEADERS = '*' # <-------- this
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000/", "http://192.168.73.153:8000/","https://20b0-2409-40c1-3002-3772-287f-3bd6-8ce2-d8bb.ngrok-free.app"]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "core",
    'rest_framework',
    'pwa',

    'compressor',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'valuation_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
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

WSGI_APPLICATION = 'valuation_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
import os.path  
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '/static/')
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, "static", 'serviceWorker.js')
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

COMPRESS_ROOT = BASE_DIR / 'static'
 
COMPRESS_ENABLED = True
 
STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',"django.contrib.staticfiles.finders.AppDirectoriesFinder")

AUTH_USER_MODEL = "core.CustomUser"

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "login"

# dqun jnfz fysa zuas
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "krishnanpandya06@gmail.com"
EMAIL_HOST_PASSWORD = "dqunjnfzfysazuas"

PWA_MANIFEST_PATH="/static/manifest.json"
PWA_APP_NAME = 'Edifice valuation'
PWA_APP_DESCRIPTION = "Edifice valuation PWA"
PWA_APP_THEME_COLOR = '#000000'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': 'https://media-hosting.imagekit.io//85437ecbfb914d28/icon-152x152.png?Expires=1836130769&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=YWJVHhnj5urZkHEesZbkUgh2lAPhmkzOyL4MuuQ-f4HSX3v7JZm2N31Q8U1B577uJCMxIMP3IenvxKWFya7SRlSB-49aBluLp~SLg8gUc7K9szGG6iqkaJekZihxtli~eXocAWDFC48KS-QGcptdC7QCBTTlpuYuL7c8cP~EUA9OuZV5E~PaUL9PaMVd0ksyVj1LFBGWaNK0ygjtXRW6bFwkF57968yxsp6mSAjRmhC26mAI2sGKCnYK3a2GdOCU1OU69~wexOb-UxiUVbF5u2uk6JNDErqQRaTS6me52loAPJkZCvbVIYN8njGfwc2Kggtc2FHqL~ZLb0LBioMTQA__',
        'sizes': '152x152'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': 'https://media-hosting.imagekit.io//85437ecbfb914d28/icon-152x152.png?Expires=1836130769&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=YWJVHhnj5urZkHEesZbkUgh2lAPhmkzOyL4MuuQ-f4HSX3v7JZm2N31Q8U1B577uJCMxIMP3IenvxKWFya7SRlSB-49aBluLp~SLg8gUc7K9szGG6iqkaJekZihxtli~eXocAWDFC48KS-QGcptdC7QCBTTlpuYuL7c8cP~EUA9OuZV5E~PaUL9PaMVd0ksyVj1LFBGWaNK0ygjtXRW6bFwkF57968yxsp6mSAjRmhC26mAI2sGKCnYK3a2GdOCU1OU69~wexOb-UxiUVbF5u2uk6JNDErqQRaTS6me52loAPJkZCvbVIYN8njGfwc2Kggtc2FHqL~ZLb0LBioMTQA__',
        'sizes': '152x152'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': 'https://media-hosting.imagekit.io//85437ecbfb914d28/icon-152x152.png?Expires=1836130769&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=YWJVHhnj5urZkHEesZbkUgh2lAPhmkzOyL4MuuQ-f4HSX3v7JZm2N31Q8U1B577uJCMxIMP3IenvxKWFya7SRlSB-49aBluLp~SLg8gUc7K9szGG6iqkaJekZihxtli~eXocAWDFC48KS-QGcptdC7QCBTTlpuYuL7c8cP~EUA9OuZV5E~PaUL9PaMVd0ksyVj1LFBGWaNK0ygjtXRW6bFwkF57968yxsp6mSAjRmhC26mAI2sGKCnYK3a2GdOCU1OU69~wexOb-UxiUVbF5u2uk6JNDErqQRaTS6me52loAPJkZCvbVIYN8njGfwc2Kggtc2FHqL~ZLb0LBioMTQA__',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'