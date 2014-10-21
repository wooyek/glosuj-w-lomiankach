# coding=utf-8
# Copyright 2013 Janusz Skonieczny
import json
import logging
from flask import request, render_template, make_response
from .. import form_next, ViewSetupError
from ..actions import BaseActionView
from ..forms import DefaultDeleteForm
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect
from flask_babel import gettext as _


def get_or_404(model, primary_key, next_url=None):
    rv = model.query.get(primary_key)
    if rv:
        return rv
    if next_url:
        return redirect(next_url)
    msg = _(u"Nie znaleziono obiektu „{}” dla klucza {}")
    raise NotFound(msg.format(model.__name__, str(primary_key)))


class BaseModelView(BaseActionView):
    model = None
    query = None
    page_size = 20
    rules = {}

    def _load_obj(self, *args, **kwargs):
        """
        Load instance based on key/id in view arguments
        """
        id = kwargs.get('id')
        return get_or_404(self.model, id)

    def _get_query(self, parent=None, order=None, *args, **kwargs):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.query:
            return self.query

        if not self.model:
            raise ViewSetupError(u"'%s' must define or 'query' or 'model'".format(self.__class__.__name__))

        self.query = self.model.query
        order = request.args.get('order', order)
        if order:
            if order.startswith("-"):
                self.query = self.query.order_by(getattr(self.model, order[1:]).desc())
            else:
                self.query = self.query.order_by(getattr(self.model, order[1:]))
        return self.query, order

    def _get_list_context(self, query, order=None, *args, **kwargs):
        """
        Get the context for this view.
        """
        page_size = int(request.args.get('page_size', self.page_size))
        if not page_size:
            # ignore paging setup if there is no page_size set
            return {'list': query}

        # offset is purely informational and ignored when during page fetching
        offset = request.args.get('offset')
        offset = int(offset) + page_size if offset else 0

        cursor = request.args.get('cursor')
        if cursor:
            raise Exception("Cursors are not supported")
            # cursor = Cursor(urlsafe=cursor)
            # seq, cursor, more = query.fetch_page(self.page_size, start_cursor=cursor)
        else:
            seq = query.offset(offset).limit(page_size).all()
            more = True     # TODO: 19.11.13 wooyek this needs improvemnts ;)
        if cursor:
            cursor = cursor.urlsafe()
        context = {
            'list': seq,
            'paginator': {'cursor': cursor, 'more': more, 'offset': offset, 'order': order},
        }
        return context

    @classmethod
    def get_rules(cls, action, view, default=None):
        """
        Add a dictionary fallback for rules declaration.
        """
        view_rules = super(BaseModelView, cls).get_rules(action, view, default=None)
        return view_rules or cls.rules.get(action, default)


class ModelView(BaseModelView):
    """CRUD actions auto generated for a given model.

    Gives meth:`list`, meth:`create_get`, meth:`create_put`, meth:`detail`,
    meth:`update_get`, meth:`update_post`, meth:`delete_get` and meth:`delete_post methods`.

    Subclass has to declare setup options and call :meth:`register_routes`::
        class MyView(ModelView):
            model = MyModel

        MyView.register(app)
    """

    templates = {}
    templates_xhr = {}
    forms = {}

    # This controller creates a fallback rule declaration method for easy rules override
    # in subclasses without the need to re-declare action method
    rules = {
        "list": [("", {})],                                     # will generate a /Model/ url without trailing 'list'
        "detail": [("<int:id>/", {})],                          # key based detail, modify this
        "create": [(None, {"methods": ['GET', 'POST']})],       # create
        "update": [("<int:id>/update", {"methods": ['GET', 'POST']})],
        "delete": [("<int:id>/delete", {"methods": ['GET', 'POST']})],
    }

    def __init__(self):
        super(ModelView, self).__init__()
        # need to copy mutable class fields to instance to avoid type wide changes
        self.templates = self.templates.copy()
        self.templates_xhr = self.templates_xhr.copy()
        self.forms = self.forms.copy()
        self.obj = None



    def list(self, *args, **kwargs):
        """
        Renders a list page
        with pagination support based on :class:`google.appengine.ext.ndb.query.Cursor`.
        :return: Responce object
        """
        query, order = self._get_query(*args, **kwargs)
        context = self._get_list_context(query, order)
        response = self._render("list", **context)
        if "paginator" in context:
            headers = {
                'X-Cursor': context['paginator']['cursor'],
                'X-Offset': context['paginator']['offset'],
            }
            response.headers.extend(headers)
        return response

    def detail(self, *args, **kwargs):
        """Renders a signdle object detail page

        :return: Responce object
        """
        self.obj = self._load_obj(*args, **kwargs)
        context = self._get_detail_context(object=self.obj)
        response = self._render("detail", **context)
        # # TODO: 19.11.13 wooyek this is silly, tiw ill not work with all models from SQLAlchemy
        # http://stackoverflow.com/questions/6745189/how-do-i-get-the-name-of-an-sqlalchemy-objects-primary-key
        # headers = {
        #     'X-PrimaryKey': self.obj.id,  #
        #     'X-Key': self.obj.key.urlsafe(),
        # }
        # response.headers.extend(headers)
        return response

    @form_next
    def create(self, *args, **kwargs):
        form = self._get_form("create", *args, **kwargs)
        next_url = request.args.get("next_url")
        if not form.validate_on_submit():
            # not valid show the form again
            return self._render("create", form=form, next_url=next_url)

        # create object and redirect to next_url or read_get
        # self.obj = self.model()
        # form.populate_obj(self.obj)
        # self.obj.put()
        self.obj = form.save()
        return redirect(self._get_create_next())

    @form_next
    def update(self, *args, **kwargs):
        self.obj = self._load_obj(*args, **kwargs)
        form = self._get_form("update", obj=self.obj, *args, **kwargs)
        next_url = request.args.get("next_url") or self.url('detail', key=self.obj.key)
        if not form.validate_on_submit():
            # not valid show the form again
            return self._render("update", form=form, object=self.obj, next_url=next_url)

        # update object and redirect to next_url or read_get
        # form.populate_obj(self.obj)
        # self.obj.put()
        form.save()
        return redirect(next_url)

    @form_next
    def delete(self, *args, **kwargs):
        try:
            self.obj = self._load_obj(*args, **kwargs)
        except NotFound:
            return redirect(self.url('list'))

        form = self._get_form("delete", obj=self.obj, default=DefaultDeleteForm, *args, **kwargs)
        if not form.validate_on_submit():
            next_url = request.args.get("next_url") or self.url('detail', key=self.obj.key.urlsafe())
            # not valid show the form again
            return self._render("delete", form=form, object=self.obj, next_url=next_url)

        # delete object and redirect to next_url or read_get
        self.obj.key.delete()
        next_url = request.args.get("next_url")
        if next_url and next_url.endswith(self.url('detail', key=self.obj.key)):
            next_url = None
        return redirect(next_url or self.url('list'))



    def _get_form(self, action, obj=None, default=None, parent=None, *args, **kwargs):
        """
        Creates an instance of form for a given action
        """
        form_class = self._get_form_class(action, default=default, *args, **kwargs)
        # query parameters can be used as initial data for the form
        form_initial_data = kwargs.pop("form_initial_data", None) or request.args
        # passing only an initial data as kwargs
        # flaskext.wft.form.Form is auto loading it's form_data from the request
        return form_class(obj=obj, model=self.model, parent=parent, **form_initial_data)

    def _get_create_next(self):
        return request.args.get("next_url") or self.url("list")

    def _get_template(self, view):
        """
        Return a template name or a template itself
        """
        if request.is_xhr:
            template = self.templates_xhr.get(view) or self.templates.get(view)
        else:
            template = self.templates.get(view)

        kind = self.controller_name()
        if view == 'list' and template is None:
            # special list template select for XHR requests
            if request.is_xhr:
                return "{}/rows.html".format(kind)
            return "{}/list.html".format(kind)

        if template is None and view in ['create', 'update']:
            # special create/update fallback
            return "{}/form.html".format(kind)

        # default template is named after view and places in folder named after model kind
        return "{}/{}.html".format(kind, view)

    def _render(self, view, **kwargs):
        """
        Renders a template and returs a Responcse instance
        """
        # assert context is not None, "RenderMixin needs context data other than None"
        template_name = self._get_template(view)
        assert template_name
        body = render_template(template_name, view=self, **kwargs)
        return make_response(body)

    def _get_detail_context(self, **kwargs):
        return kwargs





    def _get_form_class(self, action, default=None, *args, **kwargs):
        """
        Gets form_class from forms dictionary or finds a default form for a model based on model kind.
        """
        form_class = self.forms.get(action)
        if form_class:
            return form_class
        elif default:
            return default

        # forms_module = self.model.__module__.split('.', -1)[0] + ".forms"
        forms_module = self.__module__.rsplit('.', 1)[0] + ".forms"
        form_class = self.controller_name() + "Form"
        logging.debug("form_class: %s" % form_class)
        import sys

        try:
            __import__(forms_module)
            form_class = getattr(sys.modules[forms_module], form_class)
            self.forms[action] = form_class
            return form_class
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


class ModelRPC(BaseModelView):
    json_encoder = None

    # This controller creates a fallback rule declaration method for easy rules override
    # in subclasses without the need to re-declare action method
    rules = {
        "rpc": [("<int:id>/rpc", {"methods": ["GET", "PUT", "DELETE"]})],
        "search": [("search", {"methods": ["GET"]})],
    }

    def rpc(self, **kwargs):
        meth = getattr(self, "_" + request.method.lower(), None)
        # if the request method is HEAD and we don't have a handler for it
        # retry with GET
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, '_get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method
        return meth(**kwargs)

    def _get(self, id):
        obj = self._load_obj(id=id)
        rv = json.dumps(obj, indent=2, cls=self.json_encoder)
        return make_response(rv, 200, {'Content-Type': "application/json; charset=utf-8"})

    def _put(self, id):
        obj = self._load_obj(id=id)
        obj.update(**request.json)
        obj.put()
        data = {
            "success": True,
        }
        rv = json.dumps(data, cls=self.json_encoder)
        return make_response(rv, 200, {'Content-Type': "application/json; charset=utf-8"})

    def _delete(self, key):
        ndb.transaction(key.delete)
        data = {
            "success": True,
        }
        rv = json.dumps(data, cls=self.json_encoder)
        return make_response(rv, 200, {'Content-Type': "application/json; charset=utf-8"})

    def search(self, *args, **kwargs):
        query, order = self._get_query(*args, **kwargs)
        search = request.args.get('search')
        query_field = request.args.get('query_field')
        field = getattr(self.model, query_field)
        query = query.filter(field.startswith(search))
        data = self._get_list_context(query)
        data['list'] = [{"id": o.id, "cn": o.cn} for o in data['list']]
        rv = json.dumps(data, indent=2, cls=self.json_encoder)
        return make_response(rv, 200, {'Content-Type': "application/json; charset=utf-8"})



class ChildModelView(ModelView):
    parent_model = None

    @classmethod
    def get_url_prefix(cls, action=None):
        """
        Prefixes url with parent key
        """
        if action in ("list", "create"):
            return "/{}/<key:parent>/{}".format(cls.parent_model.__name__, cls.controller_name())
        return super(ChildModelView, cls).get_url_prefix(action)

    def url(self, action, **kwargs):
        if action in ("list", "create"):
            parent = self.key or getattr(self, "parent", None)
            kwargs['parent'] = parent
        return super(ChildModelView, self).url(action, **kwargs)
