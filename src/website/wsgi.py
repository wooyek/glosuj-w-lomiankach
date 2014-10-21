"""
WSGI config for website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
import logging
import os
import sys

print "Importing: %s" % __file__

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

import getpass
print "USER: ", getpass.getuser()

import socket

PRODUCTION = False if socket.gethostname() in ('ODYN',) else True
DEBUG = True


# determine where is the single absolute path that
# will be used as a reference point for other directories
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Activate Virtual Environment
try:
    import virtualenv

    VE_NAME = ".pve"
    commands = "Scripts" if sys.platform == 'win32' else "bin"
    activate_this = os.path.join(ROOT_DIR, VE_NAME, commands, "activate_this.py")
    virtualenv.logger.notify("Activating: %s" % activate_this)
    execfile(activate_this, dict(__file__=activate_this))
    # this is required for Pip to run subprocess on the VE python
    # instead of the default one, the one used to call this script
    executable = sys.executable.rsplit(os.path.sep)[-1]
    sys.executable = os.path.join(ROOT_DIR, VE_NAME, commands, executable)
except ImportError:
    logging.info("Could not import virtualenv to activate. Assuming it's already activated")

SRC_DIR = os.path.join(ROOT_DIR, 'src')
if not SRC_DIR in sys.path:
    sys.path.insert(0, SRC_DIR)

# Show a debugging info on console
logging.debug("__file__ = %s", __file__)
logging.debug("sys.version = %s", sys.version)
logging.debug("os.getpid() = %s", os.getpid())
logging.debug("os.getcwd() = %s", os.getcwd())
logging.debug("os.curdir = %s", os.curdir)
logging.debug("sys.path:\n\t%s", "\n\t".join(sys.path))
logging.debug("PYTHONPATH:\n\t%s", "\n\t".join(os.environ.get('PYTHONPATH', "").split(';')))
logging.debug("sys.modules.keys() = %s", repr(sys.modules.keys()))
logging.debug("sys.modules.has_key('website') = %s", ('website' in sys.modules))
if 'website' in sys.modules:
    logging.debug("sys.modules['website'].__name__ = %s", sys.modules['website'].__name__)
    logging.debug("sys.modules['website'].__file__ = %s", sys.modules['website'].__file__)

# # Setup proper logging
# from website.logcfg import setup_logging
#
# log_file = os.path.join(ROOT_DIR, "logs", 'website.log')
# setup_logging(log_file=log_file, console_verbosity=logging.DEBUG if PRODUCTION else logging.DEBUG)

from main import create_app, OPTIONS

try:
    application = create_app(**OPTIONS)
except Exception as ex:
    logging.error("Failed to create a WSGI app", exc_info=True)

logging.debug("app.debug: %s" % application.debug)
logging.debug("app.testing: %s" % application.testing)
