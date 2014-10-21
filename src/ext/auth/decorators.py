# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
from functools import wraps
import logging
from google.appengine.api import users
from flask import current_app
from flaskext.login import current_user


def staff_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        u = current_user
        logging.debug("User: %s" % u)
        if u.is_authenticated() and u.is_active() and (u.is_staff or users.is_current_user_admin()):
            return fn(*args, **kwargs)
        return current_app.login_manager.unauthorized()
    return decorated_view


def sysop_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        logging.debug("Sysop required: %s %s" % (users.get_current_user(), users.is_current_user_admin()))
        if users.is_current_user_admin():
            return fn(*args, **kwargs)
        return current_app.login_manager.unauthorized()
    return decorated_view
