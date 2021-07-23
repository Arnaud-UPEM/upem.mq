from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%*y05ihkqfjce6dtotz-r!e_hd-1e--7u8vyo%3_m$^y5i(v@y'

# SECURITY WARNING: define the correct hosts in production!
# ALLOWED_HOSTS = ['*'] 

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
