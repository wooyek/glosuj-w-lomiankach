# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging
import sys

from google.appengine.ext.ndb.query import Cursor
from google.appengine.ext import ndb
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView, FormMixin
from ext.utils.textutils import clear_string
from plebe.views.generic.flat import get_or_404

class AuthMixin(object):
    def auth(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            logging.debug("Anonymous redirecting from to login from: %s" % request.get_full_path)
            url = "?next=".join((reverse("login"),request.get_full_path()))
            return HttpResponseRedirect(url)

class AuthGetMixin(AuthMixin):
    def get(self, request, *args, **kwargs):
        return self.auth(request, *args, **kwargs) or super(AuthGetMixin, self).get(request, *args, **kwargs)

class AuthPostMixin(AuthMixin):
    def post(self, request, *args, **kwargs):
        return self.auth(request, *args, **kwargs) or super(AuthPostMixin, self).post(request, *args, **kwargs)

class ListView(View, TemplateResponseMixin):
    model = None
    query = None
    page_size = 20

    def get(self, request, *args, **kwargs):
        query = self.get_query()
        context = self.get_context(query=query)
        response = self.render_to_response(context)
        if context.has_key('paginator'):
            response['X-Cursor'] = context['paginator']['cursor']
            response['X-Offset'] = context['paginator']['offset']
        return response

    def get_template_names(self):
        query = self.get_query()

        template_name = self.template_name

        if not template_name:
#            model = ndb.Model._kind_map.get(query.kind)
#            app_name, model = model.__module__.split('.',1)[0], query.kind
#            template_name = "/".join((app_name, model))
            template_name = query.kind

        if not template_name.endswith(".html"):
            use_rows_template = self.request.is_ajax()
            if use_rows_template:
                template_name += "/rows.html"
            else:
                template_name += "/list.html"
        return template_name

    def get_query(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if not self.query:
            if not self.model:
                raise ImproperlyConfigured(u"'%s' must define or 'query' or 'model'" % self.__class__.__name__)
            self.query = self.model.query()
            order = self.request.GET.get('order', None)
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
            cursor = self.request.GET.get('cursor')
            offset = self.request.GET.get('offset')
            if cursor:
                cursor = Cursor(urlsafe=cursor)
                # TODO: 05.06.12 wooyek named tyiple seems to be empty in template, ivestigate
#            paginator = namedtuple('paginator', 'list cursor more')
            list, cursor, more = query.fetch_page(self.page_size, start_cursor=cursor)
            if cursor:
                cursor = cursor.urlsafe()
            offset = int(offset) + self.page_size if offset else 1
            context = {
                'list': list,
                'paginator': {'cursor': cursor, 'more': more, 'offset': offset},
            }
        context.update(kwargs)
        return context

class AuthListView(AuthGetMixin, ListView):
    pass

class SingleObjectMixin(object):
    """ Support for single model get by 'key' or 'id' keyword argument to the view """
    model   = None
    key     = None

    def get_key(self):
        if self.key:
            return self.key
        key = self.kwargs.get('key')
        logging.debug("key: %s" % key)
        id = self.kwargs.get('id')
        if key:
            self.key = ndb.Key(urlsafe=key)
        elif id:
            self.key = ndb.Key(self.model._get_kind(), int(id))
        else:
            self.key = self.request.key
        logging.debug("self.key: %s" % self.key)
        return self.key

    @cached_property
    def object(self):
        key = self.get_key()
        return get_or_404(key)

class GetMixin(object):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        assert context, "DetailView needs context data to render properly"
        response = self.render_to_response(context)
        key = self.get_key()
        response['X-KeyId'] = key.id()
        response['X-Key'] = key.urlsafe()
        return response

    def get_context_data(self, **kwargs):
        return kwargs

class DetailView(SingleObjectMixin, GetMixin, TemplateResponseMixin, View):

    def get_template_names(self):
        if self.template_name:
            return self.template_name
#        app_name, model = self.model.__module__.split('.',1)[0], self.model._get_kind()
#        return "%s/%s_detail.html" % (app_name, model)
        return self.model._get_kind() + "/detail.html"



class AuthDetailView(AuthGetMixin, DetailView):
    pass


class FormNextMixin(View):
    """
    Redirects to a form with current HTTP_REFERER info bo be used as a success_url

    This mixin needs to be before FormMixin and ProcessFormView as they override the same methods.
    """
    next        = None
    get_next    = True

    def get_success_url(self):
        url = clear_string(self.request.GET.get('next',None))
        if not url and self.success_url:
            url = self.success_url % self.object.__dict__
        if not url:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured("No URL to redirect to. Either provide a url or define a get_absolute_url method on the Model.")
        return url

    def get(self, request, *args, **kwargs):
        if self.get_next:
            self.next = clear_string(request.GET.get('next',None))
            # leave alone POST and ajax requests
            if request.method == "GET" and not request.is_ajax():
                referrer = request.META.get('HTTP_REFERER', None)
                if self.next is None and referrer is not None:
                    url = request.get_full_path()
                    if url.find("?") < 0:
                        url = "?next=".join((url, referrer))
                    else:
                        url = "&next=".join((url, referrer))
                    return HttpResponseRedirect(url)
        return super(FormNextMixin, self).get(request, *args, **kwargs)

class FormView(TemplateResponseMixin, FormNextMixin, FormMixin, ProcessFormView):
    pass

class ModelFormView(SingleObjectMixin, FormView):
    success_url = None
    form_class  = None

    def get_initial(self):
        initial = super(ModelFormView, self).get_initial()
        logging.debug("initial: %s" % initial)
        initial.update(self.request.GET.items())
        logging.debug("initial: %s" % initial)
        return initial


    def get_form_class(self):
        if self.form_class:
            return self.form_class

        forms_module = self.model.__module__.split('.', -1)[0] + ".forms"
        form_class = self.model._get_kind() + "Form"
        try:
            __import__(forms_module)
            return getattr(sys.modules[forms_module], form_class)
        except ImportError as ex:
            logging.warn(ex, exc_info=True)
            msg = "{0} could not import a default forms module '{1}'. Provide a form class or put '{2}' it in the default forms module."
            msg = msg.format(self.__class__.__name__, forms_module, form_class)
            raise ImproperlyConfigured(msg)
        except AttributeError as ex:
            logging.warn(ex, exc_info=True)
            msg = "{0} could not find a default form '{2}' in '{1}' module. Provide a form class or implement a default one."
            msg = msg.format(self.__class__.__name__, forms_module, form_class)
            raise ImproperlyConfigured(msg)


    def get_form_kwargs(self):
        kwargs = super(ModelFormView, self).get_form_kwargs()
        kwargs["model"] = self.model
        kwargs["instance"] = self.object
        return kwargs

    def get_template_names(self):
        if self.template_name:
            return self.template_name
        return "%s/form.html" % self.model._get_kind()

    def get_context_data(self, **kwargs):
        context = kwargs
        context.update({
            "object" : self.object,
            'next': self.next
        })
        return context

    def form_valid(self, form):
        # The form should decide if to create new model or update give instance
        self.object = form.save()
        return super(ModelFormView, self).form_valid(form)

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

class AuthModelFormView(AuthGetMixin, AuthPostMixin, ModelFormView):
    pass

class DeleteView(SingleObjectMixin, GetMixin, TemplateResponseMixin, FormNextMixin):
    success_url = None

    def delete(self, request, *args, **kwargs):
        self.get_key().delete()
        if request.is_ajax():
            return HttpResponse("Deleted")
        return HttpResponseRedirect(self.get_success_url())

    # Add support for browsers which only accept GET and POST for now.
    def post(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")

    def get_template_names(self):
        if self.template_name:
            return self.template_name
#        return "%s/delete.html" % self.model._get_kind()
        return "delete.html"

class AuthDeleteView(AuthGetMixin, AuthPostMixin, DeleteView):
    pass

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
            'success_url': self.delete_next,
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


class AuthCrudView(CrudView):
    list_view_class       = AuthListView
    detail_view_class     = AuthDetailView
    update_view_class     = AuthModelFormView
    create_view_class     = AuthModelFormView
    delete_view_class     = AuthDeleteView

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



