import os
from .base import *

DEBUG = True
PRODUCTION = False
BETA = True

ALLOWED_HOSTS = ['0.0.0.0', '127.0.1.1', '127.0.0.1', 'kasus.lingfil.uu.se',  'stp.lingfil.uu.se', 'cl.lingfil.uu.se']

# STATIC_ROOT = "/local/etc/httpd/html/static/swegram/dev/"
# STATIC_URL = '/static/swegram/dev/'
# STATIC_ROOT = "/opt/swegram/frontend/dist/"
STATIC_ROOT = "/home/rruan1/swegram_dev/swegram/frontend/dist/"
STATIC_URL = "/swegrambetastatic/"

'''
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': "swegram2",
        'USER': 'swegram',
        'PASSWORD': '',
        'HOST': "numerus",
        'PORT': "5432"
    }
}
'''

# To test connection with postgreql
# psql -U swegram -h 127.0.0.1 -d swegram -p 5432 -W
# enter password

# works with the following command to connect swegram2
# psql -d swegram2 -u rex -h numerus -p 5432 -W

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': 'swegram',
        'USER': 'swegram',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': "5432"
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'unique_snowflake'
    }
}

SESSION_COOKIE_AGE = 8 * 60 * 60
