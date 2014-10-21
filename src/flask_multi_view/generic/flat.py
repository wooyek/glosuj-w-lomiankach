# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
import logging

from google.appengine.ext import ndb
from google.appengine.ext.ndb.query import Cursor
import sys

from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from plebe.http.exceptions import ResponseException, Http302, Http410


def get_app_and_model_name(model):
    return (model.__module__.split('.',1)[0],model.__name__)

def delete_view(request, key, template_name=None, next=None, context={}):

    if isinstance(key, ndb.Model):
        obj = key
        key = obj.key
    else:
        obj = get_or_404(key, next)
        if not obj:
            return redirect(next)
    #model = ndb.Model._kind_map.get(key.kind())
    model = obj.__class__

    if request.method == 'POST':
        key.delete()
        if next in ('', None, '#'):
            return HttpResponse(status="204")
        return redirect(next)

    if not template_name:
        template_name = "%s/%s_confirm_delete.html" % get_app_and_model_name(model)
    template = loader.get_template(template_name)
    context = RequestContext(request, context)
    context.update({'object': obj, 'next': next})
    return HttpResponse(template.render(context))


def form_view(request, form, key=None, template_name=None, context={},  next=None, callback=None, save=True, model=None, obj=None):
    assert form, "Form argument is needed to process create, update requests for %s" % key
    if isinstance(key, ndb.Model):
        obj = key
        model = ndb.Model._kind_map.get(obj.key.kind())
    elif isinstance(key, type):
        model, key = key, None
    elif key:
        obj = get_or_404(key)
        model = ndb.Model._kind_map.get(key.kind())
    elif obj:
        model = model or ndb.Model._kind_map.get(obj.key.kind())

    if isinstance(form, type):
        form = form(data=request.POST, files=request.FILES)
    # bind and set the initial dictionary
    form.instance = obj
    form.model = model
    if request.method == 'POST':
        form.fill_data(request.POST)
        if form.is_valid():
            obj = form.save(save)
            logging.debug("obj: %s" % obj)
            if callback:
                result = callback(obj)
                if result:
                    return result
            # redirect to given next - overrides everything
            # to next set on request - a refererer used do load form
            # obj.get_absolute_url
            if isinstance(next, HttpResponse):
                return next
            next = next or getattr(request, 'next', None)
            if next:
                return HttpResponseRedirect(next)
            elif request.is_ajax():
                return HttpResponse(obj.key.urlsafe())
            elif hasattr(obj, "get_absolute_url"):
                return HttpResponseRedirect(obj.get_absolute_url())
            raise Exception(u"Nieznany adres przekierowania po udanej aktualizacji zapisie. Użyj klawisza wstecz w przeglądarce.")
    if not template_name:
        template_name = "%s/%s_form.html" % get_app_and_model_name(model)
    template = loader.get_template(template_name)
    context = RequestContext(request, context)
    context.update({'form': form, 'object': obj})
    return HttpResponse(template.render(context))


def detail_view(request, key, template_name=None, context={}):
    if isinstance(key, ndb.Model):
        obj = key
    else:
        obj = get_or_404(key)

    if not template_name:
        template_name = "%s/%s_detail.html" % get_app_and_model_name(obj.__class__)
    template = loader.get_template(template_name)
    context.update({'object': obj })
    context = RequestContext(request, context)
    return HttpResponse(template.render(context))

def list_view(request, query, context={}, page_size=50, template_name=None):
    template_name = get_list_template_name(query, template_name, request.is_ajax())
    start_cursor = request.GET.get('page')
    page_size = int(request.GET.get('page_size', page_size))
    if start_cursor:
        start_cursor = Cursor.from_websafe_string(start_cursor)
    col, cursor, more = query.fetch_page(page_size, start_cursor=start_cursor)
    d = {
        'list': col,
        'page_obj': {'has_next': more, 'next_cursor': cursor.to_websafe_string() if cursor else None }
    }
    context.update(d)
    context = RequestContext(request, context)
    template = loader.get_template(template_name)
    response = HttpResponse(template.render(context))
    if request.is_ajax() and more:
        response['X-Cursor'] = cursor.to_websafe_string()
    return response

def get_list_template_name(query, template_name, rows_template=False):
    if not template_name:
        model = query._model_class if hasattr(query, '_model_class') else ndb.Model._kind_map.get(query.kind) # nie ma modelu w nowym query
        if rows_template:
            template_name = "%s/%s_rows.html" % get_app_and_model_name(model)
        else:
            template_name = "%s/%s_list.html" % get_app_and_model_name(model)
    elif not template_name.endswith(".html"):
        if rows_template:
            template_name += "_rows.html"
        else:
            template_name += "_list.html"
    return template_name


def get_or_404(key, next=None):
    logging.debug("key: %s" % key)
    if not key:
        return None
    if isinstance(key, basestring):
        key = ndb.Key(urlsafe=key)
    o = key.get()
    if not o:
        if next:
            raise Http302(next)
        # check if there is an audit log for delete
        from audit.models import AuditLog
        audit_log = AuditLog.query(ancestor=key).filter(AuditLog.log_action == "D").get()
        if audit_log:
            msg = _(u"Obiekt „{0}” został wcześniej usunięty przez użytkownika o adresie {1}.")
            raise Http410(msg.format(key.kind(), audit_log.log_email))
        logging.warning("Http404: %s" % key.urlsafe())
        msg = _(u"No {0} was found for key {1}")
        raise Http404(msg.format(key.kind(), key.urlsafe()))
    return o

def get_or_302(key, next):
    try:
        return get_or_404(key)
    except Http404 as ex:
        logging.warn(ex, exc_info=True)
        raise ResponseException(HttpResponseRedirect(next)), None, sys.exc_info()[2]

