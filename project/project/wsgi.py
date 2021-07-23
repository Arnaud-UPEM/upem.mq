import os,sys,subprocess

virtenv = os.path.expanduser('~') + '/venv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')

try:
    if sys.version.split(' ')[0].split('.')[0] == '3':
        exec(compile(open(virtualenv, "rb").read(), virtualenv, 'exec'), dict(__file__=virtualenv))
    else:
        execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

# env = '/www/peri-alsh/services/peri-alsh/.pi.env.sh'
# env = os.path.join(virtenv, '.pi.env.sh')
# env = '.pi.env.sh'
# subprocess.call([env])

sys.path.append(os.path.expanduser('~'))
sys.path.append(os.path.expanduser('~') + '/ROOT/')
sys.path.append(os.path.expanduser('~') + '/ROOT/project/')

# os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings.dev'
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.dev')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()    


"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.dev")

# application = get_wsgi_application()
