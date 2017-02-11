# Python 2.7 required
# Use "source venv/bin/activate"

import md5
import os
import subprocess

from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)
Bootstrap(app)


@app.route('/analyse-files', methods=['POST'])
def analyse_selected_files():
    db = mongo.db.dist
    bashCommand = "peos/pml/check/pmlcheck "
    files = db.selected.find()
    for file in files:
        path = file['path']
        name = file['name']
        executeCommand = bashCommand + path
        process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        m = md5.new()
        m.update(name)
        db.analysis.insert({'name': name, 'path': path, 'process': process.communicate(), 'id': m.hexdigest()})
    return render_template('analyse.html', analyse_files=db.analysis.find())


@app.route('/select-files', methods=['POST'])
def handle_selected_files():
    db = mongo.db.dist
    files = request.form.getlist('check')
    for file in files:
        current_file = db.files.find_one({'name': file})
        if (current_file):
            path = current_file['path']
            m = md5.new()
            m.update(file)
            db.selected.insert({'name': file, 'path': path, 'id': m.hexdigest()})
    return render_template('selected.html', selected_files=db.selected.find())


@app.route('/')
def index():
    db = mongo.db.dist
    return render_template('index.html', pml_files=db.files.find())


# @param extension = ".pml"
def load_pml_source_files(path, extension):
    db = mongo.db.dist
    ext = (extension)
    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(ext)):
                if (db.files.find_one({'name': file})):
                    continue
                # search Mongo. If in Mongo, ignore. Otherwise, add.
                file_path = os.path.join(root, file)
                m = md5.new()
                m.update(file)
                db.files.insert({'name': file, 'path': file_path, 'id': m.hexdigest()})


def setup():
    db = mongo.db.dist
    db.files.drop()
    db.selected.drop()
    db.analysis.drop()
    path = os.getcwd() + "/peos"
    load_pml_source_files(path, '.pml')


if __name__ == '__main__':
    with app.app_context():
        setup()
    app.run()
