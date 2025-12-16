from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES['default']['NAME'] = os.environ.get('POSTGRES_DB', 'streamhub_db')

LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

CORS_ALLOW_ALL_ORIGINS = True
