# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging
import os

SRC_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# ============================================================================
#  a flask settings
#  http://flask.pocoo.org/docs/config/#configuring-from-files
# ============================================================================

# enable/disable debug mode
# PRODUCTION = False          # TODO: Detect if running on development server ot in production environment
# DEBUG = not PRODUCTION
# TEMPLATE_DEBUG = DEBUG
SECRET_KEY = 'jnUEFdwVexvwjpLxo20Pknka'
FLASH_MESSAGES = True


# Flask-Security
# http://pythonhosted.org/Flask-Security/configuration.html

SECURITY_PASSWORD_SALT = "abc"
# SECURITY_PASSWORD_HASH = "bcrypt"  # requires py-bcrypt
# SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_HASH = "plaintext"
SECURITY_EMAIL_SENDER = "pomoc@example.com"

SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True

SECURITY_CONFIRM_SALT = "xyz"
SECURITY_REMEMBER_SALT = "cde"
SECURITY_DEFAULT_REMEMBER_ME = True


#  Flask-WTForms settings


# Set secret keys for CSRF protection
CSRF_SESSION_KEY = 'N6612vukRUwAAHayN7SriE1T'
CSRF_ENABLED = True

# Flask-Babel
# http://pythonhosted.org/Flask-Babel/
BABEL_DEFAULT_LOCALE = "pl"
BABEL_DEFAULT_TIMEZONE = "Europe/Warsaw"

# Flask-Mail
# http://pythonhosted.org/Flask-Mail/
SERVER_EMAIL = 'Gł0suj w Łomiankach <janusz.skonieczny@dialoglomianki.pl>'

# Flask-WhooshAlchemy
# http://pythonhosted.org/Flask-WhooshAlchemy/
WHOOSH_BASE = os.path.join(SRC_DIR, ".woosh-index")

# Flask-Uploads
# http://pythonhosted.org/Flask-Uploads/

DEFAULT_FILE_STORAGE = 'filesystem'
UPLOADS_FOLDER = os.path.join(SRC_DIR, ".uploads")
FILE_SYSTEM_STORAGE_FILE_VIEW = "files"
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
