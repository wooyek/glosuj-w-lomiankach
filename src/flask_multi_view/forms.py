# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

from flask import request
from werkzeug.utils import redirect
from .basic import RenderMixin, NextMixin
from wtforms import Form


class DefaultDeleteForm(Form):
    pass


class FormMixin(object):
    """
    A mixin that provides a way to show and handle a form in a request.
    """

    initial = {}
    form_class = None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = {}
        initial.update(self.initial)
        # override initial data by GET paramters passed in the URL
        initial.update(request.attr.items())
        return self.initial

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class

    def get_form(self):
        """
        Instantiates a wtforms.form.Form class.
        """
        form_class = self.get_form_class()
        initial_data = self.get_initial()
        # passing only an initial data as kwargs
        # flaskext.wft.form.Form is auto loading it's form_data from the request
        return form_class(**initial_data)


class ProcessFormMixin(NextMixin, RenderMixin):
    """
    A mixin that processes a form on POST.
    """

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        return self.render(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return self.process_form(form, form.validate_on_submit())

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
        # PUT is a valid HTTP verb for creating (with a known URL) or editing an
        # object, note that browser forms only support POST for now.

    def process_form(self, form, is_valid):
        if is_valid:
            # maybe dot something else on xhr request
            # if request.is_xhr:
            #     return self.render_xhr()
            return redirect(self.get_next())
        return self.render(self.get_context_data(form=form))


class FormView(FormMixin, ProcessFormMixin):
    pass
