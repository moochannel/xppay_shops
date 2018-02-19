import pathlib

from .settings import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'labo.xppay.jp', 'xppay.jp']
STATIC_ROOT = '/usr/src/static/'
MEDIA_ROOT = '/usr/src/media/'
INSTALLED_APPS.remove('debug_toolbar')  # noqa
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
# SOCIAL_AUTH_DISCORD_KEY = ''
# SOCIAL_AUTH_DISCORD_SECRET = ''
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(pathlib.Path('/usr/src/db', 'db.sqlite3')),
    }
}
