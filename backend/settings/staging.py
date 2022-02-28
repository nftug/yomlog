from .base import *
import dj_database_url


DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = ['yomlog.herokuapp.com']
HOST_URL = 'https://yomlog.herokuapp.com'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

DEFAULT_FROM_EMAIL = os.environ['EMAIL_FROM']
INQUIRY_EMAIL = os.environ['EMAIL_FROM']
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
EMAIL_PORT = 587
EMAIL_USE_TLS = True

INSTALLED_APPS.append('cloudinary')
INSTALLED_APPS.append('cloudinary_storage')
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ['CLOUDINARY_CLOUD_NAME'],
    'API_KEY': os.environ['CLOUDINARY_API_KEY'],
    'API_SECRET': os.environ['CLOUDINARY_API_SECRET']
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

WEBPACK_LOADER['DEFAULT']['CACHE'] = True

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ['GOOGLE_OAUTH2_ID']
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ['GOOGLE_OAUTH2_SECRET']
# DJOSER['SOCIAL_AUTH_ALLOWED_REDIRECT_URIS'] = [
#    f'{HOST_URL}/login/social/end/google-oauth2',
# ]
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
