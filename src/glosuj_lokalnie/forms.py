# coding=utf-8
# Created 2014 by Janusz Skonieczny

from flask import url_for
from flask_wtf.form import _Auto
from wtforms import FormField
from wtforms.validators import DataRequired
from wtforms_alchemy import ModelFormField, ModelFieldList

from ext.wtf.fields import Select2Field
from ext.wtf.models import ModelForm

from . import models
from .models import DATE_FORMAT


class ApplicationForm(ModelForm):
    class Meta:
        model = models.Application
        date_format = DATE_FORMAT

    def save(self):
        self.obj = self.Meta.model()
        self.populate_obj(self.obj)
        return self.obj

    existing = 'borough', 'postal_code', 'city', 'street', 'street_no',  'flat_no'
    reg = 'reg_borough', 'reg_postal_code', 'reg_city', 'reg_street', 'reg_street_no', 'reg_flat_no'



