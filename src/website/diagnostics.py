# coding=utf-8
# Created 2014 by Janusz Skonieczny

import logging
from flask import render_template, request


def init_diagnostics(app):

    if not app.debug:
        from ext.heartbeat.logutils import AdminEmailHandler
        mail_handler = AdminEmailHandler("js@dziennik.edu.pl", "err@example.com")
        mail_handler.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(mail_handler)

    @app.errorhandler(404)
    def http404(e):
        logging.debug("e: %s" % e)
        logging.debug("request: %s" % request)
        logging.debug("request: %s" % request.url)
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def http500(e):
        logging.error(e, exc_info=True)
        logging.debug(u"request: %s" % request.url)
        logging.debug(u"request: %s" % request)
        msg = e.message or unicode(e)
        return render_template("errors/500.html", message=msg), 500

    @app.route('/favicon.ico')
    def favicon():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, "favicon.ico")

    @app.route('/_err')
    def err():
        raise Exception(u"ążśźęćńółĄŻŚŹĘŃÓŁ")

    @app.route('/_routes')
    def routes():
        links = sorted(app.url_map.iter_rules(), key=lambda rule: rule.rule)
        links = [(rule.endpoint, rule.rule) for rule in links]
        return render_template('routes.html', links=links)

    @app.route('/_styles')
    def styles():
        return render_template('styles.html')

    @app.route('/')
    def start():
        return render_template('start.html')
