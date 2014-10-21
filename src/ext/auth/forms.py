# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

from flask_babel import gettext as _
from flask_wtf import Form
from ext.wtf.fields import StringField
from wtforms.validators import URL, Email, Required


class OpenIDForm(Form):
    openid_identifier = StringField("OpenId", validators=[URL], default='http://')
    next = StringField("Next", validators=[URL], default='/')


class OpenIDRegisterForm(Form):
    email = StringField("Email", validators=[Email()])
    first_name = StringField(_(u"Imię"), validators=[Required()])
    lase_name = StringField(_(u"Nazwisko"), validators=[Required()])

class PasswordForm(Form):
    pass
