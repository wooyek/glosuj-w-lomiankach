# coding=utf-8
# Created 2014 by Janusz Skonieczny 

from datetime import datetime
import json
import sqlalchemy as sa
from sqlalchemy import orm
from website.database import db
from .pdfutils import BasePdfRendering

DATE_FORMAT2 = '%d-%m-%Y'
DATE_FORMAT = '%Y-%m-%d'


class Application(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    last_name = sa.Column(sa.String(250), info={'label': u'Nazwisko'}, nullable=False)
    first_names = sa.Column(sa.String(250), info={'label': u'Imię (imiona)'}, nullable=False)
    fathers_name = sa.Column(sa.String(250), info={'label': u'Imię ojca'}, nullable=False)
    birth_date = sa.Column(sa.Date, info={'label': u'Data urodzenia'}, nullable=False)
    pesel = sa.Column(sa.String, info={'label': u'PESEL'}, nullable=False)
    id_card_no = sa.Column(sa.String, info={'label': u'Numer dokumentu tożsamości'}, nullable=False)
    borough = sa.Column(sa.String, info={'label': u'Nazwa gminy (miasta, dzielnicy)'}, nullable=False)
    postal_code = sa.Column(sa.String, info={'label': u'Kod pocztowy'}, nullable=False)
    city = sa.Column(sa.String, info={'label': u'Miejscowość'}, nullable=False)
    street = sa.Column(sa.String, info={'label': u'Ulica'}, nullable=False)
    street_no = sa.Column(sa.String, info={'label': u'Numer domu'}, nullable=False)
    flat_no = sa.Column(sa.String, info={'label': u'Numer mieszkania'})

    reg_postal_code = sa.Column(sa.String, info={'label': u'Kod pocztowy'}, default=u"05-092", nullable=False)
    reg_city = sa.Column(sa.String, info={'label': u'Miejscowość'}, default=u"Łomianki", nullable=False)
    reg_street = sa.Column(sa.String, info={'label': u'Ulica'}, nullable=False)
    reg_street_no = sa.Column(sa.String, info={'label': u'Numer domu'}, nullable=False)
    reg_flat_no = sa.Column(sa.String, info={'label': u'Numer mieszkania'})

    def json(self):
        return {
            "last_name": self.last_name,
            "first_names": self.first_names,
            "fathers_name": self.fathers_name,
            "birth_date": self.birth_date.strftime(DATE_FORMAT),
            "pesel": self.pesel,
            "borough": self.borough,
            "id_card_no": self.id_card_no.upper(),
            "postal_code": self.postal_code,
            "city": self.city,
            "street": self.street,
            "street_no": self.street_no,
            "flat_no": self.flat_no,
            "reg_postal_code": self.postal_code or u"05-092",
            "reg_city": self.reg_city or u"Łomianki",
            "reg_street": self.reg_street,
            "reg_street_no": self.reg_street_no,
            "reg_flat_no": self.reg_flat_no,
        }

    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        birth_date = data.pop("birth_date", None)
        if birth_date:
            try:
                birth_date = datetime.strptime(birth_date, DATE_FORMAT)
            except ValueError as ex:
                birth_date = datetime.strptime(birth_date, DATE_FORMAT2)
            data["birth_date"] = birth_date
        rv = cls(**data)
        # rv.populate(**data)
        return rv


    def populate(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def pdf(self, output):
        doc = ApplicationDoc(self, output)
        return doc.render_pdf()

class ApplicationDoc(BasePdfRendering):

    def __init__(self, context, output):
        super(ApplicationDoc, self).__init__(output)
        self.context = context

    def render_pdf(self):
        self.top = self.margin
        self.page1()
        self.canvas.showPage()
        self.top = self.margin
        self.page2()
        self.canvas.showPage()
        return super(ApplicationDoc, self).render_pdf()

    def page1(self):
        self.canvas.setFont("Times New Roman", 12)
        self.text(self.context.last_name + " " + self.context.first_names)
        self.top += 1
        self.text_right(u"Burmistrz Łomianek")
        self.top += 2
        self.canvas.setFont("Times New Roman", 15)
        self.text_centered(u"WNIOSEK O WPISANIE DO REJESTRU WYBORCÓW W CZĘŚCI A")
        self.canvas.setFont("Times New Roman", 12)
        self.top += 1
        self.para(u"1. W związku z art. 18 § 9/art. 19* ustawy z dnia 5 stycznia 2011 r. – Kodeks wyborczy (Dz. U. Nr 21, poz. 112, z późn. zm.) wnoszę o wpisanie mnie do rejestru wyborców.")
        self.top += 1
        self.text(u"2. Nazwisko:")
        self.text(self.context.last_name, left=9)
        self.top += 1
        self.text(u"3. Imię (imiona):  ")
        self.text(self.context.first_names, left=9)
        self.top += 1
        self.text(u"4. Imię ojca:  ")
        self.text(self.context.fathers_name, left=9)
        self.top += 1
        self.text(u"5. Data urodzenia:  ")
        self.text(self.context.birth_date, left=9)
        self.top += 1
        self.text(u"6. Numer ewidencyjny PESEL:  ")
        self.text(self.context.pesel, left=9)
        self.top += 1
        self.text(u"7. Adres zameldowania na pobyt stały lub adres ostatniego zameldowania na pobyt stały:")
        self.text(u"a) Nazwa gminy (miasta, dzielnicy):", 1, 3)
        self.text(self.context.borough, left=10)
        self.text(u"a) Miejscowość:", 1, 3)
        self.text(self.context.city, left=10)
        self.text(u"a) Numer domu:", 1, 3)
        self.text(self.context.street_no, left=10)
        self.text(u"a) Numer mieszkania:", 1, 3)
        self.text(self.context.flat_no, left=10)
        self.text(u"Do wniosku załączam:", 2)
        self.text(u"1) kserokopię ważnego dokumentu potwierdzającego tożsamość:", 1)
        self.text(self.context.id_card_no, 1, 4)
        self.top += 1
        self.para(u"2) pisemną deklarację, o której mowa w art. 19 § 1 pkt 2 ustawy z dnia 5 stycznia 2011 r. – Kodeks wyborczy.")
        self.text(u"Data: "+datetime.now().strftime(DATE_FORMAT), 2)
        self.text_right("." * 60)
        self.text_right("podpis" + " " * 25, 1)


    def page2(self):
        self.canvas.setFont("Times New Roman", 15)
        self.text_centered(u"PISEMNA DEKLARACJA ZAWIERAJĄCA INFORMACJE")
        self.top += 0.7
        self.text_centered(u"NIEZBĘDNIE DO WPISANIA DO REJESTRU WYBORCÓW", 1)
        self.top += 1.5
        self.canvas.setFont("Times New Roman", 12)
        self.text("Łomianki, dnia " + datetime.now().strftime("%d-%m-%Y"))
        self.top += 1.5
        self.text(u"Imię (imiona):  ")
        self.text(self.context.first_names, left=6)
        self.top += 1
        self.text(u"Nazwisko:")
        self.text(self.context.last_name, left=6)
        self.top += 1.5
        self.para(u"Zgodnie z art. 19 § 1 pkt 2 ustawy z dnia 5 stycznia 2011 r. – Kodeks wyborczy (Dz. U. Nr 21, poz. 112, z poźn. zm.) oświadczam, że:")
        self.text(u"a) Posiadam obywatelstwo: Polskie", 1.5)
        self.text(u"b) stale zamieszkuję w Łomiankach", 1)
        self.text(u"kod pocztowy i miejscowość: ", 1, 3)
        self.text(str(self.context.reg_postal_code) + " " + self.context.reg_city, left=9)
        self.text(u"ulica: ", 1, 3)
        self.text(self.context.reg_street, left=9)
        self.text(u"nr domu: ", 1, 3)
        self.text(self.context.reg_street_no, left=9)
        self.text(u"nr mieszkania: ", 1, 3)
        self.text(self.context.reg_flat_no, left=9)
        self.text(u"Powyższe przekazuję w celu dołączenie do wniosku o wpisanie do rejestru wyborców", 1.5)
        self.text_right("." * 60, 4)
        self.text_right("podpis" + " " * 25, 1)
