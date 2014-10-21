# coding=utf-8
#
# Copyright 2010 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
import logging
from ext.csvutils import decode_csv_data
from flask import url_for

from wtforms import fields
from wtforms import widgets
from wtforms.fields.simple import HiddenField
from wtforms.widgets.core import HiddenInput


class StringField(fields.StringField):
    """Processes empty strings into `None`"""

    def process_formdata(self, valuelist):
        super(StringField, self).process_formdata(valuelist)
        self.data = self.data.strip()
        if not self.data:
            self.data = None


class StringListField(StringField):

    def __init__(self, *args, **kwargs):
        super(StringListField, self).__init__(*args, **kwargs)
        self.separator = kwargs.pop('separator', ', ')

    def _value(self):
        super(StringListField, self)._value()
        if isinstance(self.data, (list, tuple)):
            return self.separator.join([unicode(v) for v in self.data])
        return ''

    def process_formdata(self, valuelist):
        super(StringListField, self).process_formdata(valuelist)
        if self.data:
            self.data = [x.strip() for x in self.data.split(self.separator.strip())]
        else:
            self.data = []


class CsvDataField(StringField):
    widget = widgets.TextArea()

    def process_formdata(self, valuelist):
        super(CsvDataField, self).process_formdata(valuelist)
        logging.debug("self.data: %s" % type(self.data))
        lines = self.data

        # strip UTF-8 bom
        if lines.startswith(u'\ufeff'):
            lines = lines[1:]
        lines = lines.encode('utf-8')
        lines = lines.strip().split('\n')
        import csv
        self.data = list(decode_csv_data(csv.reader(lines, delimiter=',')))

#         for line_data in :
#             line_data
#         pack = [s.decode('utf-8').strip() for s in csv.reader(lines, delimiter=',').next()]
#         # strip UTF-8 bom
#         lines[0] = lines[0].replace(u'\ufeff', u'')
#         cache = OrderedDict()
#         for line in lines:
#             from plebe.utils.csvutils import process_csv_line
#             c1, g1, p1, p2 = process_csv_line(line, 4)
#             key = c1#".".join((c1,g1))
#             if not cache.has_key(key):
# #                phrases = CoursePhrases(course=c1, group=g1)
#                 course = CoursePhrases(course=c1, phrases={}, level=level)
#                 cache[key] = course
#             else:
#                 course = cache[key]
#             if not course.phrases.has_key(g1):
#                 course.phrases[g1] = []
#             course.phrases[g1].append(Phrase(p1, p2))
#         models = cache.values()
#         ndb.put_multi(models)
#         return models


class Select2Widget(HiddenInput):
    def __call__(self, field, **kwargs):

        return super(Select2Widget, self).__call__(field, **kwargs)


class Select2Field(HiddenField):
    widget = Select2Widget()

    def __init__(self, label=None, validators=None, filters=tuple(), description='', id=None, default=None, widget=None, _form=None, _name=None, _prefix='', _translations=None, **kwargs):
        super(Select2Field, self).__init__(label, validators, filters, description, id, default, widget, _form, _name, _prefix, _translations)
        url = kwargs.pop("url", None)
        if isinstance(url, basestring):
            url = url_for(url)
        self.url = url
        self.query_field = kwargs.pop("query_field", None)
        self.display_value = kwargs.pop("display_value", None)

    def __call__(self, **kwargs):
        logging.debug("select.url: %s" % self.url)
        logging.debug("select.url: %s" % self.query_field)
        kwargs["class_"] = "select2"
        kwargs["data_display_value"] = self.display_value
        kwargs["data_url"] = self.url
        kwargs["data_query_field"] = self.query_field
        return super(Select2Field, self).__call__(**kwargs)




