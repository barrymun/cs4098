# Python 2.7 required
# Use "source venv/bin/activate"

import logging
import os
import subprocess
from logging.handlers import RotatingFileHandler

import md5
import ontospy
from flask import Flask, render_template
from flask import request
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)
Bootstrap(app)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()


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
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info("Header = [ " + header + " ]")
            rootLogger.info("Process = [ " + process + " ]")
    return render_template('analyseowldinto.html', analyse_owl_files=db.analysisowl.find())


@app.route('/get-toplayers', methods=['POST'])
def get_toplayers():
    db = mongo.db.dist
    db.toplayers.drop()
    db.selectedowl.drop()
    owlfiles = request.form.getlist('checkowl')
    for file in owlfiles:
        current_file = db.owlfiles.find_one({'name': file})
        if (current_file):
            path = current_file['path']
            m = md5.new()
            m.update(file)
            db.selectedowl.insert({'name': file, 'path': path, 'id': m.hexdigest()})
    top_layers = db.selectedowl.find()

    for file in top_layers:
        name = file['name']
        path = file['path']
        model = ontospy.Ontospy(str(path))
        super_class_list = []
        prop_list = []
        final_link = []
        data = []
        goc = get_owl_class(model, super_class_list)
        gop = get_owl_property(model, prop_list)
        gdl = get_drug_links(model, final_link)

        for x, y in goc:
            x = str(x[40:])
            x = str(x[:-3])
            # print(x)

            for i in gdl:
                if x in str(i):
                    drug_name = str(i)[53:]
                    sep_drug_name = "'),"
                    rest_final = drug_name.split(sep_drug_name, 1)[0]
                    # print(rest_final)

            for temp in y:
                # print(temp)
                sep = "obo2:"
                rest = temp.split(sep, 1)[1]
                rest_next = rest.split(sep, 1)[1]
                rest = rest[:12]
                rest_next = rest_next[:10]
                # print(rest)
                # print(rest_next)

                for j in gop:
                    if str(rest) in str(j):
                        interaction = str(j)[18:]
                        interaction = interaction[:-2]
                        # print(interaction)

                display = rest_final + " " + interaction + " " + rest_next
                data.append(display)
                # print(display)
                # break

        m = md5.new()
        m.update(name)
        if (data != None):
            db.toplayers.insert(
                {'name': name, 'path': path, 'interactions': data, 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(data)
        else:
            db.toplayers.insert(
                {'name': name, 'path': path, 'interactions': "ERROR: no data present", 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info("INFO: no data present")
    return render_template('getowlheaders.html', toplayer_owl_files=db.toplayers.find())


@app.route('/dinto-index', methods=['GET'])
def dinto_index():
    db = mongo.db.dist
    return render_template('dintoindex.html', owl_files=db.owlfiles.find())


@app.route('/analyse-files', methods=['POST'])
def analyse_selected_files():
    db = mongo.db.dist
    db.analysis.drop()
    files = db.check.find()
    bash_command = "./peos/pml/drugfinder/drugFind "
    bash_output = "cat drug_list.txt"

    for file in files:
        path = file['path']
        name = file['name']
        execute_command = bash_command + path
        subprocess.Popen(execute_command.split(), stdout=subprocess.PIPE)
        process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        log_process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        check_process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        error_process = subprocess.Popen(bash_output.split(), stderr=subprocess.PIPE)
        log_error_process = subprocess.Popen(bash_output.split(), stderr=subprocess.PIPE)
        m = md5.new()
        m.update(name)

        if check_process.communicate()[0] != "":
            output = process.communicate()[0]
            strip_first = output[1:]
            strip_last = strip_first[:-2]
            print("OUTPUT")
            print(output)
            print(strip_last)
            print("END")
            db.analysis.insert({'name': name, 'path': path, 'process': strip_last, 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(log_process.communicate()[0])
        else:
            db.analysis.insert(
                {'name': name, 'path': path, 'process': error_process.communicate()[1], 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(log_error_process.communicate()[1])
    return render_template('analyse.html', analyse_files=db.analysis.find())


@app.route('/check-files', methods=['POST'])
def check_selected_files():
    db = mongo.db.dist
    db.check.drop()
    db.selected.drop()
    selected_files = request.form.getlist('check')
    for select_file in selected_files:
        current_file = db.files.find_one({'name': select_file})
        if (current_file):
            path = current_file['path']
            m = md5.new()
            m.update(select_file)
            db.selected.insert({'name': select_file, 'path': path, 'id': m.hexdigest()})
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
            output = process.communicate()[0]
            formatted_output = output.splitlines()
            length = len(str(path)) + 1
            result = []
            for line in formatted_output:
                formatted_line = line[length:]
                result.append(formatted_line)
            db.check.insert({'name': name, 'path': path, 'process': result, 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(log_process.communicate()[0])
        else:
            db.check.insert(
                {'name': name, 'path': path, 'process': error_process.communicate()[1], 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(log_error_process.communicate()[1])
    return render_template('check.html', check_files=db.check.find())


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


def get_owl_class(model, super_class_list):
    a_header = model.classes
    x = 0
    for i in a_header:
        ser_data = a_header[x].serialize()
        temp_sd = model.toplayer
        str_set_data = str(ser_data)
        str_set_data = str_set_data[995:]
        class_list = str_set_data.split(",")
        class_list.pop()
        super_class_list.append((str(temp_sd), class_list))
        x += 1
    return super_class_list


def get_owl_property(model, prop_list):
    a_header = model.objectProperties
    x = 0
    for i in a_header:
        prop = str(i)
        prop = prop[42:]
        prop = prop[:-2]
        data = a_header[x]
        data = data.serialize()
        str_set_data = str(data)
        str_set_data = str_set_data[833:]
        str_set_data = str_set_data[:-55]
        prop_list.append((prop, str_set_data))
        x += 1
    return prop_list


def get_drug_links(model, final_link):
    link = model.rdfgraph
    for i in link:
        if "NamedIndividual" and "DINTO" and "CHEBI" in str(i):
            if "BNode" not in str(i):
                if "XMLSchema" not in str(i):
                    if "www.w3.org" not in str(i):
                        final_link.append(i)
    return final_link


def setup():
    db = mongo.db.dist
    db.files.drop()
    db.owlfiles.drop()
    db.selected.drop()
    db.check.drop()
    db.selectedowl.drop()
    db.toplayers.drop()
    db.analysisowl.drop()
    path = os.getcwd() + "/peos/pml/drugfinder/"
    load_pml_source_files(path, '.pml')
    dinto_path = os.getcwd() + "/owl-test/"
    load_owl_source_files(dinto_path, '.owl')


if __name__ == '__main__':
    with app.app_context():
        setup()
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=0)
    logHandler.setLevel(logging.INFO)
    rootLogger.setLevel(logging.INFO)
    rootLogger.addHandler(logHandler)
    app.run(host='0.0.0.0', debug=True, port=5000)
