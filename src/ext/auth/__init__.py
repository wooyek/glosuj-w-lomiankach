# coding=utf-8
# Copyright 2014 Janusz Skonieczny
import logging

import os
from flask import current_app, flash
from flask_security import Security, SQLAlchemyUserDatastore

from .models import User, SocialConnection, Role, db


def load_user(user_id):
    return User.query.get(user_id)


def send_mail(msg):
    logging.debug("msg: %s" % msg)
    app = current_app
    mail = app.extensions.get('mail')
    if app.debug:
        flash(msg.html, "debug")
    mail.send(msg)


def init_app(app):
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    login_manager.login_view = "/login"

    # Setup Flask-Security
    security = Security()
    security = security.init_app(app, SQLAlchemyUserDatastore(db, User, Role))
    security.send_mail_task(send_mail)

    from flask_social_blueprint.core import SocialBlueprint
    SocialBlueprint.init_bp(app, SocialConnection, url_prefix="/_social")
