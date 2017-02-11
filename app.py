# Python 2.7 required
# Use "source venv/bin/activate"

from flask import Flask, Markup, render_template
from flask_bootstrap import Bootstrap
from Tkinter import Tk
from flask import request
from tkFileDialog import askopenfilename
from flask.ext.pymongo import PyMongo

import md5
import webbrowser
import os

app = Flask(__name__)
mongo = PyMongo(app)
Bootstrap(app)


@app.route('/select-files', methods=['POST'])
def handle_selected_files():
    selected_files = request.form
    files = request.form.getlist('check')
    return render_template('selected.html', files=files)

@app.route('/')
def index():
    db = mongo.db.dist
    return render_template('index.html', pml_files=db.files.find())

# @param extension = ".pml"
def load_pml_source_files(path, extension):
    ext = (extension)
    db = mongo.db.dist
    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(ext)):
                if (db.files.find_one({'name':file})):
                    continue
                # search Mongo. If in Mongo, ignore. Otherwise, add.
                file_path = os.path.join(root, file)
                m = md5.new()
                m.update(file)
                db.files.insert({'name':file, 'path':file_path, 'id':m.hexdigest()})



def setup():
    path = os.getcwd() + "/peos"
    load_pml_source_files(path, '.pml')

if __name__ == '__main__':
    with app.app_context():
        setup()
    app.run()
