# coding=utf-8
# Copyright 2013 Janusz Skonieczny

import os
from os.path import normcase

from flask_assets import Environment
from webassets import Bundle


CSS = (
    # vendor
    "vendor/font-awesome/css/font-awesome.css",
    "vendor/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css",
    # assets
    "file-uploader/fineuploader.css",
    #"select2/select2-bootstrap.css",
    "css/bootstrap.css",
    "css/bootstrap-extensions.css",
    "css/screen.css",
)

JS = (
    # vendor
    "vendor/jquery/dist/jquery.js",
    "vendor/jquery-ui/jquery-ui.js",
    "vendor/jquery-ui/ui/i18n/datepicker-pl.js",
    "vendor/bootstrap-sass-official/assets/javascripts/bootstrap.js",
    "vendor/select2/select2.js",
    "vendor/moment/moment.js",
    "vendor/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js",
    "vendor/eonasdan-bootstrap-datetimepicker/src/js/locales/bootstrap-datetimepicker.pl.js",
    # assets
    "js/html5boilerplate-logging.js",
    "js/jquery.setup.js",
    "js/widgets.js",
    "js/datetimepicker.js",
    "js/google-analitycs.js",
    "file-uploader/js/util.js",
    "file-uploader/js/button.js",
    "file-uploader/js/handler.base.js",
    "file-uploader/js/handler.form.js",
    "file-uploader/js/handler.xhr.js",
    "file-uploader/js/uploader.basic.js",
    "file-uploader/js/dnd.js",
    "file-uploader/js/uploader.js",
    "file-uploader/js/jquery-plugin.js",
)

# JS = [normcase(f) for f in JS]
# CSS = [normcase(f) for f in CSS]


def init_app(app, allow_auto_build=True):
    assets = Environment(app)
    # on google app engine put manifest file beside code
    # static folders are stored separately and there is no access to them in production
    folder = os.path.abspath(os.path.dirname(__file__)) if "APPENGINE_RUNTIME" in os.environ else ""
    assets.directory = os.path.join(app.static_folder, "compressed")
    assets.manifest = "json:{}/manifest.json".format(assets.directory)
    assets.url = app.static_url_path + "/compressed"
    compress = not app.debug  # and False
    assets.debug = not compress
    assets.auto_build = compress and allow_auto_build
    assets.register('js', Bundle(*JS, filters='yui_js', output='script.%(version)s.js'))
    assets.register('css', Bundle(*CSS, filters='yui_css', output='style.%(version)s.css'))

