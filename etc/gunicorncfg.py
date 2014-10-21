# Gunicorn configuration file
# http://docs.gunicorn.org/en/latest/configure.html#configuration-file

APP_ROOT = "/var/www/glosuj"

import getpass
print "USER: ", getpass.getuser()

# Setting documentaion
# http://docs.gunicorn.org/en/latest/settings.html#settings

proc_name = "glosuj"
workers = 1
user = "www-data"
group = "www-data"
loglevel = "debug"
bind = "unix:{}/var/gunicorn.sock".format(APP_ROOT)
debug = True
chdir = APP_ROOT + "/src"
accesslog = APP_ROOT + "/logs/gunicorn-access.log"
errorlog = APP_ROOT + "/logs/gunicorn-error.log"

