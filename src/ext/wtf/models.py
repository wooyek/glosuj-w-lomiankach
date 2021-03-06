# coding=utf-8
# Created 2014 by Janusz Skonieczny 

import logging

from flask_wtf import Form
from flask_wtf.form import _Auto
from wtforms_alchemy import model_form_factory


class FormSetupError(Exception):
    pass

BaseModelForm = model_form_factory(base=Form)


class ModelForm(BaseModelForm):
    # model = None

    def __init__(self, formdata=_Auto, obj=None, *args, **kwargs):
        self.obj = obj
        # if not self.Meta.model:
        #     self.Meta.model = kwargs.pop("model", None)
        # self.parent = kwargs.pop("parent", None)
        super(ModelForm, self).__init__(formdata=formdata, obj=obj, *args, **kwargs)

    def save(self):
        dbs = self.get_session()
        if not self.obj:
            if not self.Meta.model:
                FormSetupError("Model was not configured, please setup property or provide model during init")
            self.obj = self.Meta.model()
            dbs.add(self.obj)
        self.populate_obj(self.obj)
        dbs.commit()
        return self.obj

    def get_session(self):
        from website.database import db
        return db.session
