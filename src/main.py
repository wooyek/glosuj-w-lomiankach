# coding=utf-8
# Created 2014 by Janusz Skonieczny
import logging
import os
import sys

# Setup simple logging fast, load a more complete logging setup later on
# Log a message each time this module get loaded.

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(threadName)-8s %(message)s')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)
logging.info('Loading %s, CURRENT_VERSION_ID = %s', __name__, os.getenv('CURRENT_VERSION_ID'))


# Detect if running on development server or in production environment
# The simplest auto detection is to detect if appliaction is run from here
# production environment would use WSGI app
import socket
HOSTNAME = socket.gethostname()
DEV = (HOSTNAME.lower() in ("odyn", "thor")) or os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
PRODUCTION = __name__ != "__main__" and not DEV
GAE = "APPENGINE_RUNTIME" in os.environ
DEBUG = not PRODUCTION
TESTING = False

SRC_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)

if not PRODUCTION or not GAE:
    # there is no point in reconfiguring logging in production for gae
    # event development server with multi-process architecture is hard to grasp
    # in development server there are multiple root loggers
    # that are hard to reconfigure from here
    import website.logcfg
    log_file = os.path.join(ROOT_DIR, "logs", "website.log")
    website.logcfg.setup_logging(log_file)

TEMPLATE_FOLDER = os.path.join(ROOT_DIR, "templates")
STATIC_FOLDER = os.path.join(ROOT_DIR, "assets")
STATIC_URL = '/assets'
VENDOR_FOLDER = os.path.join(ROOT_DIR, "vendor")
VENDOR_URL = "/vendor"

# -------------------------------------------------------------
#  WSGI application
#  Put your framework initialization here
# -------------------------------------------------------------


def setup_app(debug=False, testing=False, production=False, config='dev', gae=False, **kwargs):
    from flask import Flask

    # Passing __name__ for reference point on where your code and resources are
    # This will influence a default template location
    # http://flask.pocoo.org/docs/api/#flask.Flask

    app = Flask(__name__, **kwargs)
    app.debug = debug
    # WARNING: setting True will disable login_manager decorators
    app.testing = testing

    import website.settings
    app.config.from_object(website.settings)

    import importlib
    logging.debug("Additional settings: %s" % "website.settings_"+config)
    cfg = importlib.import_module("website.settings_"+config)
    logging.debug("Loaded website.settings_%s" % config)
    app.config.from_object(cfg)

    # Enable jinja2 extensions
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.add_extension('jinja2.ext.with_')
    from ext.relative_templates import RelativeInclude
    app.jinja_env.add_extension(RelativeInclude)
    #app.jinja_env.add_extension('compressor.contrib.jinja2ext.CompressorExtension')

    if gae and not production:
        # enable jinja debugging info in GAE SDK
        # http://jinja.pocoo.org/docs/faq/#my-tracebacks-look-weird-what-s-happening
        from google.appengine.tools.devappserver2.python import sandbox
        sandbox._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']

    return app


def setup_core_extensions(app):

    from website.database import db
    db.init_app(app)

    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    import ext.auth
    import ext.auth.views
    app.register_blueprint(ext.auth.views.app)
    ext.auth.init_app(app)

    import ext.vendor
    ext.vendor.app.static_folder = VENDOR_FOLDER
    app.register_blueprint(ext.vendor.app)

    # Enable i18n and l10n
    from flask_babel import Babel
    babel = Babel(app)

    # app.config['MAIL_SUPPRESS_SEND'] = app.debug
    from flask_mail import Mail
    mail = Mail(app)

    import ext.upload
    app.register_blueprint(ext.upload.app)


def setup_blueprints(app):

    import glosuj_lokalnie.views
    app.register_blueprint(glosuj_lokalnie.views.app)



def post_initialization(app):
    """
    System blueprints that need to be initiated last
    """

    # assets must be initialized after blueprints to resolve paths correctly
    # for app engine disable auto_build, it won't work due to strict sandbox policy
    from website import assets
    assets.init_app(app, allow_auto_build=not GAE)


def setup_middleware(app, gae):

    if gae and app.debug:
        # Setup GAE Mini Profiler middleware (only enabled on dev server)
        from gae_mini_profiler import profiler, templatetags
        app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)

        @app.context_processor
        def inject_profiler():
            profiler_includes = templatetags.profiler_includes()
            return dict(profiler_includes=profiler_includes)

        if not PRODUCTION:
            # werkzeug logs tracebacks to the environ['wsgi.errors']
            # which is set to dummy StringIO by the GAE development server
            # this will ensure traceback are shown in the console

            @app.before_request
            def setup_wsgi_errors():
                from Flask import request
                request.environ['wsgi.errors'] = sys.stderr

    if app.debug:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)


def create_app(**options):
    logging.debug("setup: %s" % options)
    app = setup_app(**options)
    logging.debug("app.config: %s" % app.config)
    setup_core_extensions(app)
    setup_blueprints(app)
    post_initialization(app)
    import website.diagnostics
    website.diagnostics.init_diagnostics(app)
    setup_middleware(app, options.get("gae"))
    return app


def run_app(app, host="dev.example.com", port=4566, run_app=True):
    # for convenience in setting up OAuth ids and secretes we use the example.com domain.
    # This should allow you to circumvent limits put on localhost/127.0.0.1 usage
    # Just map dev.example.com on 127.0.0.1 ip address.

    logging.debug("app.debug: %s" % app.debug)
    logging.debug("app.testing: %s" % app.testing)
    logging.debug("run_app: %s" % run_app)
    logging.debug("Don't forget to map %s on 127.0.0.1 ip address", host)

    if not run_app:
        # we want to just return a server
        # in order to do that we need to recreate some of werkzeug functionality
        from werkzeug.serving import make_server
        server = make_server(host, port, app)
        return server

    return app.run(host, port, app)


OPTIONS = {
    "config": "prd" if PRODUCTION else "dev",
    "debug": DEBUG,
    "production": PRODUCTION,
    "testing": TESTING,
    "gae": GAE,
    "template_folder": TEMPLATE_FOLDER,
    "static_folder": STATIC_FOLDER,
    "static_url_path": STATIC_URL,
}

if __name__ == "__main__":
    OPTIONS["testing"] = "testing" in sys.argv
    app = create_app(**OPTIONS)
    run_app(app)
