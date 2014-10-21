# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import inspect
from itertools import chain
import json
import logging

from flask_wtf import Form
from werkzeug.exceptions import NotFound

from werkzeug.utils import redirect
from flask import render_template, make_response, request, url_for, flash

from . import ViewSetupError
from . import get_or_404, form_next

# __version__ = "$Rev: 73 $"[6:-2]
# $Id: actions.py,v ac929e0459b0 2013/04/02 18:03:39 wooyek $


def route(rule=None, **options):
    """Rule decorator function for class methods
    storing rule on method for later use"""
    def decorator(view):
        if hasattr(view, "rules"):
            view.rules.append((rule, options))
        else:
            view.rules = [(rule, options)]
        return view
    return decorator


def routes(app):
    def decorator(view_class):
        view_class.register_routes(app)
        return view_class
    return decorator


def decorate(fn):
    def decorator(view_class):
        view_class.decorate_actions(fn)
        return view_class
    return decorator

class BaseActionView(object):
    """Base controller configuring routes for actions defined by a subclass

    You must implement other actions::
        ButlerControler(BaseActionView):

            def hello(self, name):
                return 'Hello {}}!'.format(name)

            def greting(self, name):
                # save greeting here
                return redirect(url_for("Butler:thanks"))

            def thanks(self, name):
                return 'Thankt you {} for your greeting!'.format(name)
    """
    name = None
    decorators = {}
    rules = {}

    @classmethod
    def register_routes(cls, app):
        """
        Registers routes (build them if needed) for this controller
        """
        members = cls.find_actions()
        for name, view in members:
            rules = cls.get_rules(name, view, default=[(None, {})])
            for rule, options in rules:
                if rule is None:
                    rule = name
                rule = cls.build_rule(name, rule, view)
                endpoint = options.pop('endpoint', None) or cls.build_endpoint(name)
                proxy = cls.as_view(name, view)
                app.add_url_rule(rule, endpoint, proxy, **options)

    @classmethod
    def get_rules(cls, action, view, default=None):
        """
        Return rules for a given action view
        """
        return getattr(view, "rules", default)

    @classmethod
    def find_actions(cls):
        """
        Returns a list of methods that can be routed to
        """
        all_members = inspect.getmembers(cls, predicate=inspect.ismethod)
        # This maybe greedy, but other action selection logic would be complex and not generic anyway.
        # Override find_actions method if you don't like this one
        base_members = dir(BaseActionView)
        return [(name, f) for name, f in all_members if not name.startswith("_") and name not in base_members]

    @classmethod
    def get_url_prefix(cls, action):
        """
        Gets or creates a base (begging of) url

        By default it is "/<controller name>"
        """
        return "/" + cls.controller_name()

    @classmethod
    def build_rule(cls, action, rule, view):
        """Creates a routing rule based on either the class name (minus the 'View' suffix)
        or the defined `base_url`.

        :param rule: the path portion that should be appended to the route base or full rule staritn with „/”
        :param view: view method, rule patemters will be added based on method patemters
        """

        if rule.startswith("/"):
            # if rule has absolute path return it as is
            return rule

        parts = [cls.get_url_prefix(action)]

        # put view arguments in the rule definition
        args = inspect.getargspec(view)[0]
        import re
        for arg in args:
            # filter arguments already set in the rule
            if arg != "self" and not re.search("<(.*?:)?{}>".format(arg), rule):
                parts.append("<%s>" % arg)

        # view name or rule defined on the view is to be last int the url
        parts.append(rule)
        return "/".join(parts)

    @classmethod
    def build_endpoint(cls, action):
        return ":".join([cls.controller_name(), action])

    @classmethod
    def controller_name(cls):
        """
        Will prefix action in URL rules
        """
        if cls.name:
            return cls.name
        import re
        return re.sub("Views?|Controllers?|RPC?", "", cls.__name__)

    @classmethod
    def get_decorators(cls, action):
        decorators = cls.decorators.get(action, [])
        if not isinstance(decorators, (list, tuple)):
            decorators = [decorators]
        for_all = cls.decorators.get("_all", [])
        if not isinstance(for_all, (list, tuple)):
            for_all = [for_all]
        return chain(decorators, for_all)

    @classmethod
    def as_view(cls, action, view, *class_args, **class_kwargs):
        """
        For a given action method create a proxy view function that can be added to the routing system.
        """
        def proxy(*args, **kwargs):
            self = proxy.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(action, *args, **kwargs)

        view_name = "_".join([cls.controller_name(), action])
        if cls.decorators:
            proxy.__name__ = view_name
            proxy.__module__ = cls.__module__
            for decorator in cls.get_decorators(action):
                proxy = decorator(proxy)

        # we attach the view class to the proxy function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        proxy.view_class = cls
        proxy.__name__ = view_name
        proxy.__doc__ = view.__doc__
        proxy.__module__ = view.__module__
        return proxy

    def dispatch_request(self, action, *args, **kwargs):
        """
        Dispaches a request call to a view selected based on anction and request.method
        """
        method = request.method.lower()
        view = getattr(self, action)
        assert view is not None, 'Unimplemented view for action {} and metod {}'.format(action, method)
        return view(*args, **kwargs)

    def url(self, action, **kwargs):
        """
        Get url for action in the current view and blueprint
        """
        endpoint = self.build_endpoint(action)
        return url_for("." + endpoint, **kwargs)

    def redirect(self, action, **kwargs):
        """
        Shortcut for redirection based on action from this view.
        """
        return redirect(self.url(action, **kwargs))

    @classmethod
    def decorate_actions(cls, decorator):
        members = cls.find_actions()
        for name, view in members:
            setattr(cls, name, decorator(view))









