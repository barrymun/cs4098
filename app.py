# Python 2.7 required
# Use "source venv/bin/activate"

import logging
import md5
import os
import subprocess

import ontospy
from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)
Bootstrap(app)
bashCommand = "rm logfile.log"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
process.communicate()
LOG_FILENAME = 'logfile.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
logging.info("Active")


@app.route('/analyse-owl-files', methods=['POST'])
def analyse_owl_selected_files():
    db = mongo.db.dist
    db.analysisowl.drop()
    files = db.selectedowl.find()
    for file in files:
        name = file['name']
        path = file['path']
        model = ontospy.Ontospy(path)
        model.classes
        model.properties
        model.toplayer
        a_class = model.toplayer
        a_class = a_class[0]
        data = a_class.serialize()
        m = md5.new()
        m.update(name)
        if (data != None):
            db.analysisowl.insert({'name': name, 'path': path, 'process': data, 'id': m.hexdigest()})
            logging.info('\n')
            logging.info("Name = [ " + name + " ]")
            logging.info("Path = [ " + path + " ]")
            logging.info(data)
        else:
            db.analysisowl.insert(
                {'name': name, 'path': path, 'process': "ERROR: no data present", 'id': m.hexdigest()})
            logging.info('\n')
            logging.info("Name = [ " + name + " ]")
            logging.info("Path = [ " + path + " ]")
            logging.info("ERROR: no data present")
    return render_template('analyseowldinto.html', analyse_owl_files=db.analysisowl.find())


@app.route('/select-owl-files', methods=['POST'])
def handle_selected_owl_files():
    db = mongo.db.dist
    db.selectedowl.drop()
    owlfiles = request.form.getlist('checkowl')
    for file in owlfiles:
        current_file = db.owlfiles.find_one({'name': file})
        if (current_file):
            path = current_file['path']
            m = md5.new()
            m.update(file)
            db.selectedowl.insert({'name': file, 'path': path, 'id': m.hexdigest()})
    return render_template('selectedowldinto.html', selected_owl_files=db.selectedowl.find())


@app.route('/dinto-index', methods=['GET'])
def dinto_index():
    db = mongo.db.dist
    return render_template('dintoindex.html', owl_files=db.owlfiles.find())


@app.route('/analyse-files', methods=['POST'])
def analyse_selected_files():
    db = mongo.db.dist
    db.analysis.drop()
    bashCommand = "peos/pml/check/pmlcheck "
    files = db.selected.find()
    for file in files:
        path = file['path']
        name = file['name']
        executeCommand = bashCommand + path
        process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        log_process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        check_process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        m = md5.new()
        m.update(name)
        if (check_process.communicate()[0] != ""):
            db.analysis.insert({'name': name, 'path': path, 'process': process.communicate()[0], 'id': m.hexdigest()})
            logging.info('\n')
            logging.info("Name = [ " + name + " ]")
            logging.info("Path = [ " + path + " ]")
            logging.info(log_process.communicate()[0])
        else:
            db.analysis.insert(
                {'name': name, 'path': path, 'process': "ERROR: PML file format incorrect", 'id': m.hexdigest()})
            logging.info('\n')
            logging.info("Name = [ " + name + " ]")
            logging.info("Path = [ " + path + " ]")
            logging.info("ERROR: PML file format incorrect")
    return render_template('analyse.html', analyse_files=db.analysis.find())


@app.route('/select-files', methods=['POST'])
def handle_selected_files():
    db = mongo.db.dist
    db.selected.drop()
    files = request.form.getlist('check')
    for file in files:
        current_file = db.files.find_one({'name': file})
        if (current_file):
            path = current_file['path']
            m = md5.new()
            m.update(file)
            db.selected.insert({'name': file, 'path': path, 'id': m.hexdigest()})
    return render_template('selected.html', selected_files=db.selected.find())


@app.route('/index', methods=['GET'])
def index():
    db = mongo.db.dist
    return render_template('index.html', pml_files=db.files.find())


@app.route('/')
def main():
    return render_template('home.html')


# @param extension = ".owl"
def load_owl_source_files(path, extension):
    db = mongo.db.dist
    ext = (extension)
    for root, dirs, owlfiles in os.walk(path):
        for file in owlfiles:
            if (file.endswith(ext)):
                if (db.owlfiles.find_one({'name': file})):
                    continue
                # search Mongo. If in Mongo, ignore. Otherwise, add.
                file_path = os.path.join(root, file)
                m = md5.new()
                m.update(file)
                db.owlfiles.insert({'name': file, 'path': file_path, 'id': m.hexdigest()})


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
    db.selectedowl.drop()
    db.analysisowl.drop()
    path = os.getcwd() + "/peos"
    load_pml_source_files(path, '.pml')
    dinto_path = os.getcwd()
    load_owl_source_files(dinto_path, '.owl')


if __name__ == '__main__':
    with app.app_context():
        setup()
    app.run()
