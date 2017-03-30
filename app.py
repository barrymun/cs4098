# Python 2.7 required
# Use "source venv/bin/activate"

import logging
import md5
import os
import re
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
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()


@app.route('/get-toplayers', methods=['POST'])
def get_toplayers():
    db = mongo.db.dist
    db.toplayers.drop()
    db.selectedowl.drop()
    owl_files = request.form.getlist('checkowl')
    pml_info = db.analysis.find()
    pml_info_drug_list = []

    for pmlinfo in pml_info:
        value = str(pmlinfo['process'])
        value = value[1:]
        value = value[:-1]
        while "," in value:
            value = value[1:]
            sep_drug_name = ","
            value_current = value.split(sep_drug_name, 1)[0]
            value = value.split(sep_drug_name, 1)[1]
            if "(" not in value_current:
                if ":" not in value_current:
                    if ")" not in value_current:
                        pml_info_drug_list.append(value_current)

    for file in owl_files:
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
        links_list = []
        goc = get_owl_class(model, super_class_list)
        gop = get_owl_property(model, prop_list)
        gdl = get_drug_links(model, final_link)
        actual_drug_name = ""

        if len(pml_info_drug_list) == 1:
            for x, y in goc:
                class_to_string = str(x[39:])
                class_to_string = class_to_string[:-2]

                for i in gdl:
                    if class_to_string in str(i):
                        drug_name = str(i)[53:]
                        sep_drug_name = "'),"
                        actual_drug_name = drug_name.split(sep_drug_name, 1)[0]
                        break

                for user_selected_elem in pml_info_drug_list:
                    if user_selected_elem in actual_drug_name:
                        for temp in y:
                            sep = "obo2:"
                            rest = temp.split(sep, 1)[1]
                            rest_next = rest.split(sep, 1)[1]
                            rest = rest[:12]
                            rest_next = rest_next[:-1]
                            interaction = ""

                            for j in gop:
                                if str(rest) in str(j):
                                    interaction = str(j)[18:]
                                    interaction = interaction[:-2]

                            display = actual_drug_name + " " + interaction + " " + rest_next
                            if "CHEBI" in rest_next:
                                links_list.append(rest_next)
                            data.append(display)

        elif len(pml_info_drug_list) > 1:
            drug_name_list = []
            for x, y in goc:
                class_to_string = str(x[39:])
                class_to_string = class_to_string[:-2]

                for i in gdl:
                    if class_to_string in str(i):
                        drug_name = str(i)[53:]
                        sep_drug_name = "'),"
                        actual_drug_name = drug_name.split(sep_drug_name, 1)[0]
                        for j in pml_info_drug_list:
                            if j in actual_drug_name:
                                drug_name_list.append((class_to_string, actual_drug_name))

                for a, b in drug_name_list:
                    for elem in pml_info_drug_list:
                        if elem not in b:
                            for el in y:
                                sep = "obo2:"
                                rest = el.split(sep, 1)[1]
                                rest = rest[:12]
                                if a in el:
                                    for j in gop:
                                        if rest in j:
                                            interaction = str(j)[18:]
                                            interaction = interaction[:-2]
                                            display = b + " " + interaction + " " + elem
                                            data.append(display)

        m = md5.new()
        m.update(name)

        if (data != None):
            db.toplayers.insert(
                {'name': name, 'path': path, 'interactions': data, 'links': links_list, 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(data)
        else:
            db.toplayers.insert(
                {'name': name, 'path': path, 'interactions': "ERROR: no data present", 'links': links_list,
                 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info("INFO: no data present")
    return render_template('getowlheaders.html', toplayer_owl_files=db.toplayers.find())


@app.route('/dinto-index', methods=['GET'])
def dinto_index():
    db = mongo.db.dist
    return render_template('dintoindex.html', owl_files=db.owlfiles.find())


@app.route('/characterization-analysis-results', methods=['POST'])
def get_characterization_analysis_results():
    db = mongo.db.dist
    db.selectedcharacterization.drop()
    db.characterizationanalysisfiles.drop()
    char_files = request.form.getlist('checkchar')
    pml_info = db.analysis.find()
    m = md5.new()
    drug_list = ""
    path = ""

    # list
    for pi in pml_info:
        drug_list = pi['process']
        break

    print(drug_list)
    drug_list = re.sub('[(]', '', drug_list)
    drug_list = re.sub('[)]', '', drug_list)
    drug_list = re.sub('[[]', '', drug_list)
    drug_list = re.sub('[]]', '', drug_list)
    # drug_list = drug_list.translate(None, '[()]')
    print(drug_list)
    drug_list_to_list = drug_list.split(",")

    for file in char_files:
        current_file = db.characterizationfiles.find_one({'name': file})
        if (current_file):
            path = current_file['path']
            m.update(file)
            db.selectedcharacterization.insert({'name': file, 'path': path, 'id': m.hexdigest()})

    display = []
    l = len(drug_list_to_list)
    count = 1

    with open(path) as f:
        for line in f:
            for drug in drug_list_to_list:
                if drug in line:
                    if count is l:
                        print("HELLO")
                        print(line)
                        line_to_list = line.split(",")
                        # line = re.sub('[[]', '', line)
                        # line = re.sub('[\n]', '', line)
                        # print(line)
                        display.append(line_to_list)
                    count += 1
            count = 1

    print(display)
    db.characterizationanalysisfiles.insert({'result': display, 'id': m.hexdigest()})
    rootLogger.info('\n')
    rootLogger.info("Result = [ " + str(display) + " ]")
    return render_template('charanalysisresults.html',
                           char_analysis_files=db.characterizationanalysisfiles.find())


@app.route('/ddi-characterization-index', methods=['GET'])
def characterization_index():
    db = mongo.db.dist
    return render_template('characterizationindex.html',
                           characterizationfiles_files=db.characterizationfiles.find())


@app.route('/kb-system-selection', methods=['GET'])
def kb_system_selection():
    return render_template('kbsystemselection.html')


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
        m = md5.new()
        m.update(name)
        execute_command = bash_command + path
        subprocess.Popen(execute_command.split(), stdout=subprocess.PIPE)
        process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        log_process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        check_process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        error_process = subprocess.Popen(bash_output.split(), stderr=subprocess.PIPE)
        log_error_process = subprocess.Popen(bash_output.split(), stderr=subprocess.PIPE)

        if check_process.communicate()[0] != "":
            output = process.communicate()[0]
            strip_first = output[1:]
            strip_last = strip_first[:-2]
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


def sequence_flatten(file):
    count = 1
    bracket_count = 0
    reversed_bracket_count = 0
    sequence_to_remove = []

    f = open(file, "r")
    lines = f.readlines()
    print(lines)
    print("")
    f.close()

    f = open(file, "w")
    for line in lines:
        if "{" in line:
            bracket_count += 1
        if "}" in line:
            bracket_count -= 1
        if "sequence" in line:
            if count is 2:
                sequence_to_remove.append(line)
                for rev_line in reversed(lines):
                    if "}" in rev_line:
                        reversed_bracket_count += 1
                    if "{" in rev_line:
                        reversed_bracket_count -= 1
                    if bracket_count is reversed_bracket_count:
                        sequence_to_remove.append(rev_line)
                        break
            else:
                count += 1
        f.write(line)
    f.close()

    for str in sequence_to_remove:
        print(str)

    rev_count = 1

    f = open(file, "r")
    lines2 = f.readlines()
    # print(lines2)
    f.close()

    f = open(file, "w")
    for line2 in lines2:
        if line2 not in sequence_to_remove:
            f.write(line2)
        else:
            sequence_to_remove.remove(line2)
    f.close()

    # NEW
    next_line_action = 0
    previous_line_tab_count = 0
    tabs = 0

    f = open(file, "r")
    lines2 = f.readlines()
    # print(lines2)
    f.close()

    f = open(file, "w")
    for line in lines2:
        if "action" in line:
            if previous_line_tab_count is 0:
                previous_line_tab_count = line.count('\t')
            if next_line_action is 1:
                if previous_line_tab_count < line.count('\t'):
                    tabs = line.count('\t')
            next_line_action = 1
        f.write(line)
    print(tabs)
    f.close()

    # reducing tab count
    f = open(file, "r")
    lines2 = f.readlines()
    # print(lines2)
    f.close()

    f = open(file, "w")
    for line in lines2:
        if line.count('\t') >= tabs:
            if tabs is not 0:
                line = line[1:]
        f.write(line)
    f.close()

    # fix for no closing bracket
    previous_line_tab_count = 0
    next_bracket_action = 0
    f = open(file, "r")
    lines2 = f.readlines()
    # print(lines2)
    f.close()

    f = open(file, "w")
    for line in lines2:
        if "action" in line:
            if previous_line_tab_count is 0:
                previous_line_tab_count = line.count('\t')
            if next_line_action is 1:
                if previous_line_tab_count is line.count('\t'):
                    tab_string = ""
                    for i in range(line.count('\t')):
                        tab_string += "\t"
                    tab_string += "}\n"
                    f.write(tab_string)
            next_line_action = 1
        else:
            previous_line_tab_count = 0
            next_line_action = 0

        f.write(line)
    f.close()

    # fix for no closing bracket
    previous_line_tab_count = 0
    next_bracket_action = 0
    f = open(file, "r")
    lines2 = f.readlines()
    # print(lines2)
    f.close()

    f = open(file, "w")
    for line in lines2:
        if line.strip() is "}":
            if previous_line_tab_count is 0:
                previous_line_tab_count = line.count('\t')
            if next_bracket_action is 1:
                if previous_line_tab_count is line.count('\t'):
                    line = ""
                    next_bracket_action = 0
            else:
                next_bracket_action = 1
        else:
            previous_line_tab_count = 0
            next_bracket_action = 0
        f.write(line)
    f.close()


def remove_blank(file):
    f = open(file, "r")
    lines = f.readlines()
    f.close()

    f = open(file, "w")
    for line in lines:
        if line.rstrip() is not "":
            f.write(line)
    f.close()


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

    # for loop no longer required here, but the functionality for
    # multiple file selections can exist while this remains
    for file in files:
        path = file['path']
        remove_blank(path)
        name = file['name']
        m = md5.new()
        m.update(name)
        line_number = 1
        construct_duplication_check = []

        # check for un-named construct here
        with open(path) as f:
            for line in f:
                if "action" in line:
                    keyword = "action"
                    line = line.split(keyword, 1)[1]
                    line = line.split("{", 1)[0]
                    line = line.strip()
                    if line not in construct_duplication_check:
                        construct_duplication_check.append(line)
                    else:
                        duplication_error_string = "PML contains construct DUPLICATION (" + str(
                            line_number) + ", " + line + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': duplication_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(duplication_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=duplication_error_string)
                    if len(line) < 1:
                        unnamed_error_string = "PML contains UN-NAMED construct (" + str(
                            line_number) + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': unnamed_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(unnamed_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=unnamed_error_string)
                elif "task" in line:
                    keyword = "task"
                    line = line.split(keyword, 1)[1]
                    line = line.split("{", 1)[0]
                    line = line.strip()
                    if line not in construct_duplication_check:
                        construct_duplication_check.append(line)
                    else:
                        duplication_error_string = "PML contains construct DUPLICATION (" + str(
                            line_number) + ", " + line + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': duplication_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(duplication_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=duplication_error_string)
                    if len(line) < 1:
                        unnamed_error_string = "PML contains UN-NAMED construct (" + str(
                            line_number) + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': unnamed_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(unnamed_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=unnamed_error_string)
                elif "sequence" in line:
                    keyword = "sequence"
                    line = line.split(keyword, 1)[1]
                    line = line.split("{", 1)[0]
                    line = line.strip()
                    if line not in construct_duplication_check:
                        construct_duplication_check.append(line)
                    else:
                        duplication_error_string = "PML contains construct DUPLICATION (" + str(
                            line_number) + ", " + line + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': duplication_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(duplication_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=duplication_error_string)
                    if len(line) < 1:
                        unnamed_error_string = "PML contains UN-NAMED construct (" + str(
                            line_number) + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': unnamed_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(unnamed_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=unnamed_error_string)
                elif "branch" in line:
                    keyword = "branch"
                    line = line.split(keyword, 1)[1]
                    line = line.split("{", 1)[0]
                    line = line.strip()
                    if line not in construct_duplication_check:
                        construct_duplication_check.append(line)
                    else:
                        duplication_error_string = "PML contains construct DUPLICATION (" + str(
                            line_number) + ", " + line + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': duplication_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(duplication_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=duplication_error_string)
                    if len(line) < 1:
                        unnamed_error_string = "PML contains UN-NAMED construct (" + str(
                            line_number) + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': unnamed_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(unnamed_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=unnamed_error_string)
                elif "selection" in line:
                    keyword = "selection"
                    line = line.split(keyword, 1)[1]
                    line = line.split("{", 1)[0]
                    line = line.strip()
                    if line not in construct_duplication_check:
                        construct_duplication_check.append(line)
                    else:
                        duplication_error_string = "PML contains construct DUPLICATION (" + str(
                            line_number) + ", " + line + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': duplication_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(duplication_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=duplication_error_string)
                    if len(line) < 1:
                        unnamed_error_string = "PML contains UN-NAMED construct (" + str(
                            line_number) + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': unnamed_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(unnamed_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=unnamed_error_string)
                elif "iteration" in line:
                    keyword = "iteration"
                    line = line.split(keyword, 1)[1]
                    line = line.split("{", 1)[0]
                    line = line.strip()
                    if line not in construct_duplication_check:
                        construct_duplication_check.append(line)
                    else:
                        duplication_error_string = "PML contains construct DUPLICATION (" + str(
                            line_number) + ", " + line + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': duplication_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(duplication_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=duplication_error_string)
                    if len(line) < 1:
                        unnamed_error_string = "PML contains UN-NAMED construct (" + str(
                            line_number) + ", " + keyword + ")"
                        db.check.insert(
                            {'name': name, 'path': path,
                             'process': unnamed_error_string,
                             'id': m.hexdigest()})
                        rootLogger.info('\n')
                        rootLogger.info("Name = [ " + name + " ]")
                        rootLogger.info("Path = [ " + path + " ]")
                        rootLogger.info(unnamed_error_string)
                        return render_template('check.html', check_files=db.check.find(),
                                               msg_string=unnamed_error_string)
                line_number += 1

        executeCommand = bashCommand + path
        process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        log_process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        check_process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
        error_process = subprocess.Popen(executeCommand.split(), stderr=subprocess.PIPE)
        log_error_process = subprocess.Popen(executeCommand.split(), stderr=subprocess.PIPE)

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
            return render_template('check.html', check_files=db.check.find(), msg_string="CLEAR")
        else:
            db.check.insert(
                {'name': name, 'path': path, 'process': error_process.communicate()[1], 'id': m.hexdigest()})
            rootLogger.info('\n')
            rootLogger.info("Name = [ " + name + " ]")
            rootLogger.info("Path = [ " + path + " ]")
            rootLogger.info(log_error_process.communicate()[1])
            return render_template('check.html', check_files=db.check.find(), msg_string="ERROR")


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


# @param extension = ".csv"
def load_characterization_source_files(path, extension):
    db = mongo.db.dist
    ext = extension
    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(ext)):
                if (db.characterizationfiles.find_one({'name': file})):
                    continue
                # search Mongo. If in Mongo, ignore. Otherwise, add.
                file_path = os.path.join(root, file)
                m = md5.new()
                m.update(file)
                db.characterizationfiles.insert({'name': file, 'path': file_path, 'id': m.hexdigest()})


def get_owl_class(model, super_class_list):
    a_header = model.classes
    x = 0
    for i in a_header:
        ser_data = a_header[x].serialize()
        temp_sd = model.toplayer[x]
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
    db.characterizationfiles.drop()
    db.selectedcharacterization.drop()
    db.characterizationanalysisfiles.drop()
    path = os.getcwd() + "/peos/pml/drugfinder/pml-test-files"
    load_pml_source_files(path, '.pml')
    dinto_path = os.getcwd() + "/owl-test/"
    load_owl_source_files(dinto_path, '.owl')
    characterization_path = os.getcwd() + "/characterization-files"
    load_characterization_source_files(characterization_path, '.csv')


if __name__ == '__main__':
    with app.app_context():
        setup()
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=0)
    logHandler.setLevel(logging.INFO)
    rootLogger.setLevel(logging.INFO)
    rootLogger.addHandler(logHandler)
    app.run(host='0.0.0.0', debug=True, port=5000)
