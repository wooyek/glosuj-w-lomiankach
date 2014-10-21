# coding=utf-8
# Copyright 2014 Janusz Skonieczny
import logging
import tempfile
import os
from reportlab import rl_config
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

PARA_STYLE = ParagraphStyle(name='Normal', fontName="Times New Roman", fontSize=12, leading=15, alignment=TA_JUSTIFY)


class BasePdfRendering(object):
    def __init__(self, output):
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.width, self.height = portrait(A4)
        self.y = self.height
        self.margin = 2.5
        self.x = self.margin
        self.pdf = output or tempfile.TemporaryFile()
        times_new_roman = os.path.join(self.base_path, "templates", "fonts", "times.ttf")
        times_new_roman_bold = os.path.join(self.base_path, "templates", "fonts", "timesbd.ttf")
        pdfmetrics.registerFont(TTFont('Times New Roman', times_new_roman))
        pdfmetrics.registerFont(TTFont('Times New Roman Bold', times_new_roman_bold))

        self.canvas = canvas.Canvas(self.pdf, pagesize=portrait(A4))

    def render_pdf(self):
        logging.debug("render_pdf: Saving")
        self.canvas.save()
        rl_config._reset()

    @property
    def top(self):
        return (self.height - self.y) / cm

    @top.setter
    def top(self, value):
        self.y = self.height - float(value) * cm


    def get_cols(self):
        inner_width = 13.5 * cm
        margin = (self.width - inner_width) / 2
        x = inner_width / 6
        col1 = margin + x
        col2 = margin + 3 * x
        col3 = margin + 5 * x
        return col1 / cm, col2 / cm, col3 / cm


    def img(self, image, margin_top=0, left=None, width=None, height=None):
        image = os.path.join(self.base_path, 'templates', 'img', image)
        logging.debug("self.top: %s" % self.top)
        self.top += (margin_top + height)
        logging.debug("self.top: %s" % self.top)
        x = left * cm if left else self.center(width)
        self.canvas.drawImage(image, x, self.y, width=width * cm, height=height * cm)

    def center(self, width):
        return (self.width - width * cm) / 2

    def text_centered(self, s, margin_top=0, left=None, ):
        x = left * cm if left else self.width / 2
        self.canvas.drawCentredString(x, self.y, s)

    def text_right(self, txt, margin_top=0, right=None, fill_to=None):
        x = self.width - (right if right else self.margin) * cm
        self.top += margin_top
        self.canvas.drawRightString(x, self.y, txt)

    def text(self, txt, margin_top=0, left=None, fill_to=None):
        if not txt:
            return
        x = (left if left else self.margin) * cm
        self.top += margin_top
        self.canvas.drawString(x, self.y, txt, )
        if fill_to:
            self.dot_fill(x, fill_to * cm, txt)

    def dot_fill(self, left, right, txt):
        # How big is a space?
        space = self.canvas.stringWidth(' ', self.canvas._fontname, self.canvas._fontsize)

        # How big is a dot?
        dot = self.canvas.stringWidth(' .', self.canvas._fontname, self.canvas._fontsize)

        # How long is the text
        txtw = self.canvas.stringWidth(txt, self.canvas._fontname, self.canvas._fontsize)

        # How much space do I have to fill?
        extra = right - txtw - left

        # How many whole dots will that take?
        dots = int((extra - space - space) / dot)
        self.canvas.drawRightString(right, self.y, ' .' * dots)

    def para(self, txt, margin=None, style=PARA_STYLE):
        p = Paragraph(txt, style)
        margin = margin or self.margin
        aw = self.width - (2 * margin * cm)
        ah = self.y - margin * cm
        logging.info("ah: %s" % (ah / cm))
        w, h = p.wrap(aw, ah)
        logging.info("h: %s" % (h / cm))
        self.y -= h
        p.drawOn(self.canvas, margin * cm, self.y)
