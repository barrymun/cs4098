# Python 2.7 required
# Use "source venv/bin/activate"

import logging
import md5
import os
import subprocess
from logging.handlers import RotatingFileHandler

import ontospy
from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)
Bootstrap(app)
remove_logfile = "rm info.log"
remove_logfile_process = subprocess.Popen(remove_logfile.split(), stdout=subprocess.PIPE)
remove_logfile_process.communicate()
remove_logfile_errors = "rm info.log.1"
remove_logfile_errors_process = subprocess.Popen(remove_logfile_errors.split(), stdout=subprocess.PIPE)
remove_logfile_errors_process.communicate()


@app.route('/analyse-owl-files', methods=['POST'])
def analyse_owl_selected_files():
    db = mongo.db.dist
    db.analysisowl.drop()
    files = request.form.getlist('checkheaders')
    for file in files:
        current_file = db.toplayers.find_one({'header': file})
        if (current_file):
            name = current_file['name']
            path = current_file['path']
            header = current_file['header']
            process = current_file['process']
            m = md5.new()
            m.update(file)
            db.analysisowl.insert(
                {'name': name, 'path': path, 'header': header, 'process': process, 'id': m.hexdigest()})
            app.logger.info('\n')
            app.logger.info("Name = [ " + name + " ]")
            app.logger.info("Path = [ " + path + " ]")
            app.logger.info("Header = [ " + header + " ]")
            app.logger.info("Process = [ " + process + " ]")
    return render_template('analyseowldinto.html', analyse_owl_files=db.analysisowl.find())


@app.route('/get-toplayers', methods=['POST'])
def get_toplayers():
    db = mongo.db.dist
    db.toplayers.drop()
    top_layers = db.selectedowl.find()
    for file in top_layers:
        name = file['name']
        path = file['path']
        model = ontospy.Ontospy(path)
        a_header = model.toplayer
        x = 0
        for i in a_header:
            data = str(a_header[x])
            process = str(a_header[x].serialize())
            m = md5.new()
            m.update(name)
            if (data != None):
                db.toplayers.insert(
                    {'name': name, 'path': path, 'header': data, 'process': process, 'id': m.hexdigest()})
                app.logger.info('\n')
                app.logger.info("Name = [ " + name + " ]")
                app.logger.info("Path = [ " + path + " ]")
                app.logger.info("Header = [ " + data + " ]")
                app.logger.info("Process = [ " + process + " ]")
                app.logger.info(data)
            else:
                db.toplayers.insert(
                    {'name': name, 'path': path, 'header': "ERROR: no data present",
                     'process': "ERROR: no data present", 'id': m.hexdigest()})
                app.logger.info('\n')
                app.logger.info("Name = [ " + name + " ]")
                app.logger.info("Path = [ " + path + " ]")
                app.logger.info("Header = [ " + data + " ]")
                app.logger.info("Process = [ " + process + " ]")
                app.logger.info("ERROR: no data present")
            x += 1
    return render_template('getowlheaders.html', toplayer_owl_files=db.toplayers.find())


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
        error_process = subprocess.Popen(executeCommand.split(), stderr=subprocess.PIPE)
        log_error_process = subprocess.Popen(executeCommand.split(), stderr=subprocess.PIPE)
        m = md5.new()
        m.update(name)
        if (check_process.communicate()[0] != ""):
            db.analysis.insert({'name': name, 'path': path, 'process': process.communicate()[0], 'id': m.hexdigest()})
            app.logger.info('\n')
            app.logger.info("Name = [ " + name + " ]")
            app.logger.info("Path = [ " + path + " ]")
            app.logger.info(log_process.communicate()[0])
        else:
            db.analysis.insert(
                {'name': name, 'path': path, 'process': error_process.communicate()[1], 'id': m.hexdigest()})
            app.logger.info('\n')
            app.logger.info("Name = [ " + name + " ]")
            app.logger.info("Path = [ " + path + " ]")
            app.logger.info(log_error_process.communicate()[1])
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
    db.toplayers.drop()
    db.analysisowl.drop()
    path = os.getcwd() + "/peos"
    load_pml_source_files(path, '.pml')
    dinto_path = os.getcwd()
    load_owl_source_files(dinto_path, '.owl')


if __name__ == '__main__':
    with app.app_context():
        setup()
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)
    logHandler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(logHandler)
    app.run(host='0.0.0.0', debug=True, port=5000)
