# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

from flask import render_template, request, make_response
from flask.views import MethodView
from werkzeug.utils import redirect


class RenderMixin(object):
    """
    Get template name and render.
    """
    template = None

    def get_template(self):
        """ Return a template name or a template itself """
        return self.template

    def render(self, context=None):
        """
        Renders a template and returs a Responcse instance
        """
        # assert context is not None, "RenderMixin needs context data other than None"
        template_name = self.get_template()
        assert template_name
        body = render_template(template_name, **context or {})
        return make_response(body)

    def get_context_data(self, **kwargs):
        return kwargs


class NextMixin(MethodView):
    """
    Redirects to a form with current HTTP_REFERER info bo be used as a success_url

    This mixin needs to be before FormMixin and ProcessFormView as they override the same methods.
    """
    next = None

    def get_next(self):
        return self.next or request.args.get('next', None)

    def get(self, *args, **kwargs):
        next = self.get_next()
        # POST and ajax requests do not need next
        if not next and request.method == "GET" and not request.is_xhr:
                referrer = request.headers.get('HTTP_REFERER', None)
                if referrer is not None:
                    url = request.url
                    if url.find("?") < 0:
                        url = "?next=".join((url, referrer))
                    else:
                        url = "&next=".join((url, referrer))
                    return redirect(url)
        return super(NextMixin, self).get(request, *args, **kwargs)
