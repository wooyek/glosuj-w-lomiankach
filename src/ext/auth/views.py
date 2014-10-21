# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
import logging

from flask import Blueprint, render_template, current_app
from flask_login import login_required

from flask_multi_view import actions
from flask_multi_view.extensions.sqlachemy import ModelRPC, ModelView

from .models import User

app = Blueprint("auth", __name__, template_folder="templates")


@actions.routes(app)
class UserView(ModelView):
    model = User


@actions.routes(app)
class UserRPC(ModelRPC):
    model = User


@login_required
@app.route("/profile")
def profile():
    return render_template('User/profile.html')

