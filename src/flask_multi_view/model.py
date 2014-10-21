# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging

from flask import render_template, request
from flask.views import MethodView
from werkzeug.utils import cached_property, redirect

from . import ViewSetupError
from .basic import RenderMixin, NextMixin
from .forms import FormView
from . import get_or_404


class ListView(MethodView, RenderMixin):
    model = None
    query = None
    page_size = 20

    def get(self, request, *args, **kwargs):
        query = self.get_query()
        context = self.get_context(query=query)
        response = self.render(context)
        if 'paginator' in context:
            headers = {
                'X-Cursor': context['paginator']['cursor'],
                'X-Offset': context['paginator']['offset'],
            }
            response.headers.extend(headers)
        return response

    def get_query(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.query:
            return self.query

        if not self.model:
            raise ViewSetupError(u"'%s' must define or 'query' or 'model'".format(self.__class__.__name__))

        self.query = self.model.query()
        order = request.args.get('order', None)
        if order:
            if order.startswith("-"):
                self.query = self.query.order(-self.model._properties[order[1:]])
            else:
                self.query = self.query.order(self.model._properties[order])
        return self.query

    def get_context(self, **kwargs):
        """
        Get the context for this view.
        """
        query = kwargs.pop('query')
        if not self.page_size:
            context = {'list': query}
        else:
            # offset is purely informational and ignored when during page fetching
            offset = request.args.get('offset')
            offset = int(offset) + self.page_size if offset else 1

            cursor = request.args.get('cursor')
            if cursor:
                cursor = Cursor(urlsafe=cursor)
            seq, cursor, more = query.fetch_page(self.page_size, start_cursor=cursor)
            if cursor:
                cursor = cursor.urlsafe()
            context = {
                'list': seq,
                'paginator': {'cursor': cursor, 'more': more, 'offset': offset},
            }
        context.update(kwargs)
        return context

    def get_kind(self):
        if self.model:
            return self.model._get_kind()
        if self.query:
            return self.query.kind

    def get_template(self):
        template_name = self.template or self.get_kind()

        if not template_name.endswith(".html"):
            use_rows_template = request.is_xhr()
            if use_rows_template:
                template_name += "/rows.html"
            else:
                template_name += "/list.html"
        return template_name


class SingleObjectMixin(object):
    """ Support for single model get by 'key' or 'id' keyword argument to the view """
    model = None

    def get_key(self, *args, **kwargs):
        key = kwargs.get('key')
        logging.debug("key: %s" % key)
        integer_id = kwargs.get('id')
        if key:
            return ndb.Key(urlsafe=key)
        if id:
            return ndb.Key(self.model._get_kind(), int(integer_id))

    @cached_property
    def object(self):
        key = self.get_key()
        return get_or_404(key)


class DetailView(SingleObjectMixin, RenderMixin, MethodView):

    def get(self, *args, **kwargs):
        context = self.get_context_data(object=self.object, **kwargs)
        response = self.render(context)
        key = self.get_key(*args, **kwargs)
        headers = {
            'X-KeyId': key.id(),
            'X-Key': key.urlsafe(),
        }
        response.headers.extend(headers)
        return response

    def get_context_data(self, **kwargs):
        return kwargs

    def get_template(self):
        if self.template:
            return self.template
        return self.model._get_kind() + "/detail.html"


class ModelFormView(SingleObjectMixin, FormView):

    def get_form_class(self):
        if self.form_class:
            return self.form_class

        forms_module = self.model.__module__.split('.', -1)[0] + ".forms"
        form_class = self.model._get_kind() + "Form"
        import sys
        try:
            __import__(forms_module)
            return getattr(sys.modules[forms_module], form_class)
        except ImportError as ex:
            logging.warn(ex, exc_info=True)
            msg = "{0} could not import a default forms module '{1}'. Provide a form class or put '{2}' it in the default forms module."
            msg = msg.format(self.__class__.__name__, forms_module, form_class)
            raise ViewSetupError(msg)
        except AttributeError as ex:
            logging.warn(ex, exc_info=True)
            msg = "{0} could not find a default form '{2}' in '{1}' module. Provide a form class or implement a default one."
            msg = msg.format(self.__class__.__name__, forms_module, form_class)
            raise ViewSetupError(msg)

    def get_template_names(self):
        if self.template:
            return self.template
        return "%s/form.html" % self.model._get_kind()

    def get_context_data(self, **kwargs):
        context = kwargs
        context.update({
            "object" : self.object,
            'next': self.next
        })
        return context

    def process_form(self, form, is_valid):
        if is_valid:
            # The form should decide if to create new model or update give instance
            self.object = form.save()
        return super(ModelFormView, self).process_form(form, is_valid)

    def get(self, request, *args, **kwargs):
        response = super(ModelFormView, self).get(request, *args, **kwargs)
        obj = self.object
        if obj:
            key = obj.key
            response['X-KeyId'] = key.id()
            response['X-Key'] = key.urlsafe()
        return response

    def post(self, request, *args, **kwargs):
        response = super(ModelFormView, self).post(request, *args, **kwargs)
        obj = self.object
        if obj:
            key = obj.key
            response['X-KeyId'] = key.id()
            response['X-Key'] = key.urlsafe()
        return response


class DeleteView(SingleObjectMixin, RenderMixin, NextMixin):

    def get(self, *args, **kwargs):
        context = self.get_context_data(object=self.object, **kwargs)
        responce = self.render(context)
        key = self.get_key(*args, **kwargs)
        headers = {
            'X-KeyId': key.id(),
            'X-Key': key.urlsafe(),
        }
        responce.headers.extend(headers)
        return responce

    def delete(self, request, *args, **kwargs):
        key = self.get_key()
        key.delete()
        if request.is_ajax():
            return "Key {} deleted".format(key.urlsafe()), 204
        return redirect(self.get_next())

    def post(self, *args, **kwargs):
        """ Shadows delete method """
        return self.delete(*args, **kwargs)

    def get_template(self):
        if self.template:
            return self.template
        return self.model._get_kind() + "/delete.html"


# class AuthDeleteView(AuthGetMixin, AuthPostMixin, DeleteView):
#     pass
#
# class AuthMixin(object):
#     def auth(self, request, *args, **kwargs):
#         if request.user.is_anonymous():
#             logging.debug("Anonymous redirecting from to login from: %s" % request.get_full_path)
#             url = "?next=".join((reverse("login"),request.get_full_path()))
#             return HttpResponseRedirect(url)
#
# class AuthGetMixin(AuthMixin):
#     def get(self, request, *args, **kwargs):
#         return self.auth(request, *args, **kwargs) or super(AuthGetMixin, self).get(request, *args, **kwargs)
#
# class AuthPostMixin(AuthMixin):
#     def post(self, request, *args, **kwargs):
#         return self.auth(request, *args, **kwargs) or super(AuthPostMixin, self).post(request, *args, **kwargs)
# class AuthListView(AuthGetMixin, ListView):
#     pass
# class AuthDetailView(AuthGetMixin, DetailView):
#     pass
# class AuthModelFormView(AuthGetMixin, AuthPostMixin, ModelFormView):
#     pass


class CrudView(object):
    """A helper class to build CRUD urls based on generic views"""
    model           = None
    form_class      = None
    delete_next     = None
    list_query      = None
    list_view_class       = ListView
    detail_view_class     = DetailView
    update_view_class     = ModelFormView
    create_view_class     = ModelFormView
    delete_view_class     = DeleteView
    urls_type       = "id"

    def __init__(self, model, **kwargs):
        self.model = model
        # this way subclasses won't have to implement their own constructor
        # just to save arguments in properties
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def list_view(self, **initkwargs):
        kwargs = {
            'model': self.model,
            'list_query': self.list_query,
        }
        kwargs.update(initkwargs)
        kwargs['query'] = kwargs.pop('list_query')
        return self.list_view_class.as_view(**kwargs)

    def create_view(self, **initkwargs):
        kwargs = {
            'model': self.model,
            'get_next': False,
        }
        kwargs.update(initkwargs)
        return self.create_view_class.as_view(**kwargs)

    def update_view(self, **initkwargs):
        kwargs = {
            'model': self.model,
            'form_class': self.form_class,
        }
        kwargs.update(initkwargs)
        return self.update_view_class.as_view(**kwargs)

    def detail_view(self, **initkwargs):
        kwargs = {
            'model': self.model,
        }
        kwargs.update(initkwargs)
        return self.detail_view_class.as_view(**kwargs)

    def delete_view(self, **initkwargs):
        kwargs = {
            'model': self.model,
            'next': self.delete_next,
        }
        kwargs.update(initkwargs)
        return self.delete_view_class.as_view(**kwargs)

    def urls(self):
        from django.conf.urls import patterns, url
        kind = self.model._get_kind()
        prefix = "^" + kind
        if self.urls_type == "key":
            return patterns('',
                url(prefix+"/$", self.list_view(), name=kind+"_list"),
                url(prefix+"/create$", self.create_view(), name=kind+"_create"),
                url(prefix+"/(?P<key>[-\w]+)/$", self.detail_view(), name=kind+"_detail"),
                url(prefix+"/(?P<key>[-\w]+)/update$", self.update_view(), name=kind+"_update"),
                url(prefix+"/(?P<key>[-\w]+)/delete$", self.delete_view(success_url=prefix+"/$"), name=kind+"_delete"),
            )
        return patterns('',
            url(prefix+"/$", self.list_view(), name=kind+"_list"),
            url(prefix+"/create$", self.create_view(), name=kind+"_create"),
            url(prefix+"/(?P<id>\d+)/$", self.detail_view(), name=kind+"_detail"),
            url(prefix+"/(?P<id>\d+)/update$", self.update_view(), name=kind+"_update"),
            url(prefix+"/(?P<id>\d+)/delete$", self.delete_view(success_url=prefix+"/$"), name=kind+"_delete"),
        )


class Put2PostMixin(object):
    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class RpcCreateView(SingleObjectMixin, View):
    model = None
    def post(self, request, *args, **kwargs):
        obj = self.create_object(request.POST)
        obj.put()
        return HttpResponse(obj.key.urlsafe())

    def create_object(self, properties):
        properties = dict([(k, properties[k]) for k in properties.keys()])
        parent = properties.pop("parent", None)
        if parent:
            parent = ndb.Key(urlsafe=parent)
        return self.model(parent=parent, **properties)

    def validate(self, property, value):
        return value

class RpcSetView(SingleObjectMixin, View):
    def post(self, request, *args, **kwargs):
        self.update_properties(request.POST)
        self.object.put()
        return HttpResponse(self.object.key.urlsafe())

    def update_properties(self, properties):
        property = properties.get('property', None)
        if property:
            value = properties.get('value')
            self.validate(property, value)
        else:
            for property, value in properties.items():
                setattr(self.object, property, value)

    def validate(self, property, value):
        return value



