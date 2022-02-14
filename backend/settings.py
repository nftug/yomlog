from pathlib import Path
import os
from datetime import timedelta
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

except:
    from .secret_local import *

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

    # 3rd party apps
    'rest_framework',
    'djoser',
    'django_filters',
    'corsheaders',
    'webpack_loader',
    'social_django',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'debug_toolbar',

    # My applications
    'apiv1.apps.Apiv1Config',
    'backend.apps.BackendConfig',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    # '127.0.0.1',
]


ROOT_URLCONF = 'backend.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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

LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = BASE_DIR + '/staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'

# For Debug Only!
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'JWT_ALLOW_REFRESH': True,
    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
    )
}

# CORS
if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ORIGIN_WHITELIST = (
        'http://localhost:8080',
        'http://127.0.0.1:8080',
    )

AUTH_USER_MODEL = 'backend.CustomUser'

DJOSER = {
    'USER_CREATE_PASSWORD_RETYPE': True,
    # 'SEND_ACTIVATION_EMAIL': True,
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SERIALIZERS': {
        'user': 'auth.serializers.CustomUserListSerializer',
        'current_user': 'auth.serializers.CustomUserSerializer',
        'user_create_password_retype': 'auth.serializers.CustomUserCreateSerializer',
    },
    'HIDE_USERS': False,
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': [
        'http://localhost:8000/login/social/end/google-oauth2',
    ]
}

if DEBUG:
    SESSION_COOKIE_SECURE = False
else:
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Social Login
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_OAUTH2_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = GOOGLE_OAUTH2_SECRET

SOCIAL_AUTH_RAISE_EXCEPTIONS = False

try:
    DEFAULT_FROM_EMAIL = os.environ['EMAIL_FROM']
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True

except:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    HOST_URL = 'http://localhost:8000'
