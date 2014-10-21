# coding=utf-8
# Copyright 2013 Janusz Skonieczny
from flask import current_app, Blueprint

app = Blueprint("vendor", __name__, static_folder="../vendor")

@app.route('/vendor/<path:filename>')
def vendor(filename):
    """
    A separate static-like handler for bower vendor folder
    """
    from flask import send_from_directory
    return send_from_directory("vendor", filename)
