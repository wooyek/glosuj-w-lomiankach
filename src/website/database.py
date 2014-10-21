# coding=utf-8
# Copyright 2013 Janusz Skonieczny

# This module is wide used dependency also in main.py
# it's separate from main.py to spare any circular imports pain and weirdness

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

