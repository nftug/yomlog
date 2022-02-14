from .base import *
from .secret_local import *


DEBUG = True
ALLOWED_HOSTS = ['*']
HOST_URL = 'http://localhost:8000'

INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = [
    # '127.0.0.1',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8080',
    'http://127.0.0.1:8080',
)

SESSION_COOKIE_SECURE = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
HOST_URL = 'http://localhost:8000'

WEBPACK_LOADER['DEFAULT']['CACHE'] = False

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_OAUTH2_ID
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = GOOGLE_OAUTH2_SECRET
# DJOSER['SOCIAL_AUTH_ALLOWED_REDIRECT_URIS'] = [
#    'http://localhost:8000/login/social/end/google-oauth2',
# ]
