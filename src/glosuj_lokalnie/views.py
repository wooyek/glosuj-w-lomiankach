# coding=utf-8
# Created 2014 by Janusz Skonieczny
import json
import logging

from werkzeug.utils import redirect
from flask import request, render_template, make_response, url_for
from flask.blueprints import Blueprint
from flask_multi_view import actions
from flask_multi_view.actions import BaseActionView
from flask_multi_view.extensions.sqlachemy import ModelView, ModelRPC

from website.database import db
from .models import Application
from .pdfutils import BasePdfRendering

app = Blueprint("glosuj_lokalnie", __name__, template_folder="templates")
COOKIE_NAME = 'wniosek2'


@actions.routes(app)
class ApplicationView(ModelView):
    model = Application

    # @actions.route("create", methods=['GET'])
    def create(self, *args, **kwargs):
        data = request.cookies.get(COOKIE_NAME)
        obj = Application.from_json(data) if data else None
        form = self._get_form("create", obj=obj)
        next_url = request.args.get("next_url")
        if not form.validate_on_submit():
            # not valid show the form again
            return self._render("create", form=form, next_url=next_url)

        self.obj = form.save()
        rv = redirect(url_for(".Application:pdf"))
        data = json.dumps(self.obj, default=lambda o: o.json())
        rv.set_cookie(COOKIE_NAME, data)
        return rv

    @actions.route("pdf", methods=['GET'])
    def pdf(self, **kwargs):
        data = request.cookies.get(COOKIE_NAME)
        if data:
            data = json.loads(data)
            logging.debug("data: %s" % data)
            if not data:
                return redirect(url_for('.Application:create'))
        application = Application()
        logging.debug("application: %s" % application)
        application.populate(**data)
        from StringIO import StringIO
        output = StringIO()
        application.pdf(output)
        output = output.getvalue()
        rv = make_response(output)
        rv.headers['Content-Type'] = 'application/pdf'
        name = 'Wniosek-o-wpisanie-do-rejestru-wyborcow'
        rv.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % name
        return rv

    def pdf2(self, **kwargs):
        data = request.cookies.get(COOKIE_NAME)
        data = json.loads(data)
        logging.debug("data: %s" % data)
        if not data:
            return redirect(url_for('.Application:create'))

        from xhtml2pdf import pisa
        from StringIO import StringIO
        html = render_template('Application/pdf.html', object=data)
        logging.debug("html: %s" % html)
        rv = StringIO()
        pdf = pisa.CreatePDF(StringIO(html.encode('utf-8')), rv)
        logging.debug("pdf.err: %s" % pdf.err)
        logging.debug("pdf: %s" % pdf)
        rv = make_response(rv.getvalue())
        rv.headers['Content-Type'] = 'application/pdf'
        name = 'Wniosek o wpisanie do rejestru wyborcow'
        rv.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % name

        return rv

@app.route("/polityka-prywatnosci")
def polityka():
    return render_template("polityka.html")


@app.route('/sitemap.xml')
def sitemap():
    return render_template("sitemap2.xml")
