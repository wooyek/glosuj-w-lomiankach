# coding=utf-8
# Copyright 2013 Janusz Skonieczny
from flask.helpers import make_response
import os
from flask import Blueprint, render_template, request, url_for
from flask.globals import current_app
# from flask_uploads import Upload, save, delete
from werkzeug.utils import redirect, secure_filename

app = Blueprint("files", __name__, template_folder="templates")

# TODO: 29.11.13 wooyek

def allowed_file(filename):
    allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    uf = request.files['file']
    if uf and allowed_file(uf.filename):
        filename = secure_filename(uf.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        uf.save(os.path.join(upload_folder, filename))
        return redirect(url_for(',view', filename=filename))

@app.route('/upload', methods=['POST'])
def upload():
    save(request.files['upload'])
    return redirect(url_for('.view'))


@app.route('/delete/<int:filename>', methods=['POST'])
def remove(filename):
    """Delete an uploaded file."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.remove(os.path.join(upload_folder, filename))
    return make_response("Deleted", 200)


@app.route("/<path:filename>")
def view(filename):
    from flask import send_from_directory
    folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(folder, filename)
