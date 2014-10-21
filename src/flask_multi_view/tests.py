# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import unittest

import flask
from flask import Response
from flask_multi_view.extensions.sqlachemy import ModelView
from jinja2 import Template

from .basic import NextMixin, RenderMixin


class RenderMixinTests(unittest.TestCase):
    def test_render(self):
        mixin = RenderMixin()
        app = flask.Flask(__name__)
        with app.test_request_context('/'):
            self.assertRaises(AssertionError, mixin.render)
        with app.test_request_context('/'):
            self.assertRaises(AssertionError, mixin.render)
            mixin.template = Template("foo bar")
            response = mixin.render()
            self.assertIsInstance(response, Response)


class NextMixinTests(unittest.TestCase):

    def test_next_provided(self):
        app = flask.Flask(__name__)
        with app.test_request_context('/?next=a'):
            mixin = NextMixin()
            self.assertEqual(mixin.get_next(), 'a')
        with app.test_request_context('/?next=a', headers=[('HTTP_REFERER', 'c')]):
            mixin = NextMixin()
            self.assertEqual(mixin.get_next(), 'a')

    def test_next_hardwired(self):
        app = flask.Flask(__name__)
        with app.test_request_context('/?next=a', headers=[('HTTP_REFERER', 'c')]):
            mixin = NextMixin()
            mixin.next = "b"
            self.assertEqual(mixin.get_next(), 'b')

    def test_no_next(self):
        app = flask.Flask(__name__)
        with app.test_request_context('/', ):
            mixin = NextMixin()
            self.assertIsNone(mixin.get_next())
            self.assertRaises(AttributeError, mixin.get, "super 'get' method should not be implemented")

    def test_next_refferrer(self):
        app = flask.Flask(__name__)
        with app.test_request_context('/', headers=[('HTTP_REFERER', 'c')]):
            mixin = NextMixin()
            self.assertIsNone(mixin.get_next())
            responce = mixin.get()
            self.assertEqual(responce.status_code, 302)
            self.assertEqual(responce.headers['Location'], 'http://localhost/?next=c')

class FormTests(unittest.TestCase):
    def test_form(self):
        a = ModelView()
        b = ModelView()
        self.assertEqual(id(a.page_size), id(b.page_size))
        self.assertNotEqual(id(a.forms), id(b.forms))
        a.forms["update"] = object()
        self.assertFalse(b.forms.has_key("update"))
