# coding=utf-8
# Copyright 2013 Janusz Skonieczny

import logging
import os

from flask import request, current_app

MSG = u'''
Message type: %(levelname)s
Location:     %(pathname)s:%(lineno)d
Module:       %(module)s
Function:     %(funcName)s
Time:         %(asctime)s

Message:

%(message)s
'''

EXTRA_MSG = u"""
URL: {url}
REF: {ref}

Headers: {headers}

environ: {environ}

"""

HTML = u"""
<p>URL: {url}</p
<p>REF: {ref}</p>

{msg}

<p>Headers</p>
<table style="border-collapse: collapse;">{headers}</table>

<p>Environ</p>
<table style="border-collapse: collapse;">{environ}</table>
"""

TD = u'<tr><td style="white-space:nowrap; border: 1px solid #CCC; padding: 4px;">{key}</td><td style="border: 1px solid #CCC;">{value}</td><tr>'

class AdminEmailHandler(logging.Handler):
    """An exception log handler that emails log entries to site admins.

    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.

    Based on django.utils.log.AdminEmailHandler
    """

    def __init__(self, to, sender, include_html=True):
        logging.Handler.__init__(self)
        self.include_html = include_html
        self.sender = sender
        self.to = to
        from logging import Formatter
        self.setFormatter(Formatter(MSG))


    def format_message(self, record):
        msg = self.format(record)
        body = EXTRA_MSG.format(url=request.url, ref=request.headers.get("Referer"), headers=request.headers, environ=request.environ) + msg
        headers = "".join([TD.format(key=k, value=v) for k, v in request.headers.items()])
        environ = "".join([TD.format(key=k, value=v) for k, v in request.environ.items()])
        msg = "<br/>".join(msg.split("\n"))
        html = HTML.format(url=request.url, ref=request.headers.get("Referer"), headers=headers, environ=environ, msg=msg)
        return body, html

    def emit(self, record):
        subject = self.format_subject(record)
        body, html = self.format_message(record)
        logging.debug("html_message: %s" % body)
        self.send_message(self.sender, self.to, subject, body, html)

    def send_message(self, sender, to, subject, body, html):
        if "APPENGINE_RUNTIME" in os.environ:
            return self._gae_admin_send(sender, to, subject, body, html)
        return self._extension_send(sender, to, subject, body, html)

    def _gae_admin_send(self, sender, to, subject, body, html):
        from google.appengine.api.mail import send_mail_to_admins
        send_mail_to_admins(sender, subject, body, html)

    def _gae_send(self, sender, to, subject, body, html):
        from google.appengine.api.mail import EmailMessage
        message = EmailMessage()
        message.sender = sender
        message.subject = subject
        message.body = body
        message.html = html
        message.to = to
        try:
            message.send()
        except Exception as ex:
            logging.warning(ex, exc_info=ex)

    def _extension_send(self, sender, to, subject, body, html):
        from flask_mail import Message
        message = Message()
        message.sender = sender
        message.subject = subject
        message.body = body
        if html:
            message.html = html
        message.to = to
        try:
            current_app.extensions['mail'].send(message)
        except Exception as ex:
            logging.warning(ex, exc_info=ex)


    def format_subject(self, record):
        """
        Escape CR and LF characters, and limit length.
        RFC 2822's hard limit is 998 characters per line. So, minus "Subject: "
        the actual subject must be no longer than 989 characters.
        """
        subject = record.getMessage()
        formatted_subject = subject.replace('\n', '\\n').replace('\r', '\\r')
        return formatted_subject[:989]
