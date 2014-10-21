# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
import functools
from flask import request

from flask_babel import gettext as _, ngettext as __
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect


def get_or_404(key, next=None):
    o = key.get()
    if not o:
        if next:
            return redirect(next)
        msg = _(u"Nie znaleziono obiektu „{}” dla klucza {}")
        raise NotFound(msg.format(key.kind(), key.urlsafe()))
    return o


def form_next(view):
    """
    Decorator for views using query parameter `next` for cancel or success redirect.
    Redirects to the current URL adding `next` if referrer URL is available.
    Does nothing if current request has next parameter already or Referer is None
    """
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        next = request.args.get('next_url', "").strip()
        # POST and ajax requests do not need next
        if not next and request.method == "GET" and not request.is_xhr:
            referrer = request.headers.get('Referer', None)
            if referrer is not None:
                url = request.url
                if url.find("?") < 0:
                    url = "?next_url=".join((url, referrer))
                else:
                    url = "&next_url=".join((url, referrer))
                return redirect(url)
        return view(*args, **kwargs)
    return wrapper


class ViewSetupError(Exception):
    pass
