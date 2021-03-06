from .settings import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'labo.xppay.jp', 'xppay.jp']
STATIC_ROOT = '/usr/src/static/'
MEDIA_ROOT = '/usr/src/media/'
INSTALLED_APPS.remove('debug_toolbar')  # noqa
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
