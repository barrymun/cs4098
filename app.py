# Python 2.7 required
# Use "source venv/bin/activate"

import hashlib
import logging
import md5
import os
import re
import subprocess
import time
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


def pml_tx_parallelize_sequence(origin_filename):
    destination_filename = "temp_parallelize.pml"

    destination_resource = open(destination_filename, 'w')

    with open(origin_filename) as f:
        content = f.readlines()

    BASH_COMMAND = "rm temp_parallelize.pml"
    SEQUENCE_IDENTIFIER = "sequence"
    ITERATION_IDENTIFIER = "iteration"
    BRANCH_IDENTIFIER = "branch"
    ACTION_IDENTIFIER = "action"
    PROCESS_IDENTIFIER = "process"
    SELECTION_IDENTIFIER = "selection"

    IDENTIFIERS = [
        SELECTION_IDENTIFIER,
        SEQUENCE_IDENTIFIER,
        BRANCH_IDENTIFIER,
        ACTION_IDENTIFIER,
        PROCESS_IDENTIFIER,
        ITERATION_IDENTIFIER
    ]

    OPENING_BRACKET = "{"
    CLOSING_BRACKET = "}"

    m = hashlib.md5()

    def get_units(content):
        units = []
        non_meta_structure_open = False
        unit = ""
        for i, line in enumerate(content):
            line_stripped = "".join(line.split())
            if (non_meta_structure_open and line_stripped == CLOSING_BRACKET):
                unit += line
                units.append(unit)
                non_meta_structure_open = False
                unit = ""
            elif (SELECTION_IDENTIFIER in line and not non_meta_structure_open):
                identifier_start_index = line.index(SELECTION_IDENTIFIER)
                identifier_end_index = identifier_start_index + len(SELECTION_IDENTIFIER)
                line = line[:identifier_end_index] + " " + "a" + m.hexdigest() + " " + "{\n"
                unit += line
                non_meta_structure_open = True
            elif (BRANCH_IDENTIFIER in line and not non_meta_structure_open):
                identifier_start_index = line.index(BRANCH_IDENTIFIER)
                identifier_end_index = identifier_start_index + len(BRANCH_IDENTIFIER)
                line = line[:identifier_end_index] + " " + "a" + m.hexdigest() + " " + "{\n"
                unit += line
                non_meta_structure_open = True
            elif (ACTION_IDENTIFIER in line and not non_meta_structure_open):
                identifier_start_index = line.index(ACTION_IDENTIFIER)
                identifier_end_index = identifier_start_index + len(ACTION_IDENTIFIER)
                line = line[:identifier_end_index] + " " + "a" + m.hexdigest() + " " + "{\n"
                unit += line
                non_meta_structure_open = True
            elif non_meta_structure_open:
                unit += line
            m.update(str(time.time()))
        return units

    units = get_units(content)

    process_line = ""

    for i, line in enumerate(content):
        if PROCESS_IDENTIFIER in line:
            process_line = line
            break

    m.update(str(time.time()))
    destination_resource.write(process_line)
    temp = "b" + m.hexdigest()
    destination_resource.write("\tbranch %s {\n" % temp)

    for i, j in enumerate(units):
        destination_resource.write(j)

    destination_resource.write("\t}\n")
    destination_resource.write("}")
    destination_resource.close()

    open(origin_filename, 'w').close()
    origin_filename = open(origin_filename, 'w')
    branch_check = 0

    with open(destination_filename) as f:
        for line in f:
            if branch_check is 0:
                origin_filename.write(line)
                if "branch" in line:
                    branch_check = 1
            else:
                if "branch" not in line:
                    branch_check = 0
                    origin_filename.write(line)
    origin_filename.close()
    process = subprocess.Popen(BASH_COMMAND.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]


def pml_tx_unroll_iteration(origin_filename):
    destination_filename = "temp_unroll.pml"
    with open(origin_filename) as f:
        content = f.readlines()

    BASH_COMMAND = "rm temp_unroll.pml"
    SEQUENCE_IDENTIFIER = "sequence"
    ITERATION_IDENTIFIER = "iteration"
    BRANCH_IDENTIFIER = "branch"
    ACTION_IDENTIFIER = "action"
    PROCESS_IDENTIFIER = "process"
    SELECTION_IDENTIFIER = "selection"

    IDENTIFIERS = [
        SELECTION_IDENTIFIER,
        SEQUENCE_IDENTIFIER,
        BRANCH_IDENTIFIER,
        ACTION_IDENTIFIER,
        PROCESS_IDENTIFIER,
    ]

    OPENING_BRACKET = "{"
    CLOSING_BRACKET = "}"

    def get_process_line(content):
        for i, line in enumerate(content):
            if PROCESS_IDENTIFIER in line:
                break
        return line

    non_meta_structure_open = False

    m = hashlib.md5()
    units = []

    unit = ""
    for i, line in enumerate(content):
        line_stripped = "".join(line.split())
        if (non_meta_structure_open and line_stripped == CLOSING_BRACKET):
            unit += line
            units.append(unit)
            non_meta_structure_open = False
            unit = ""
        elif (SELECTION_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(SELECTION_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(SELECTION_IDENTIFIER)
            line = line[:identifier_end_index] + " " + "a" + m.hexdigest() + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif (BRANCH_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(BRANCH_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(BRANCH_IDENTIFIER)
            line = line[:identifier_end_index] + " " + "a" + m.hexdigest() + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif (ACTION_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(ACTION_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(ACTION_IDENTIFIER)
            line = line[:identifier_end_index] + " " + "a" + m.hexdigest() + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif non_meta_structure_open:
            unit += line
        m.update(str(time.time()))

    destination_file = open(destination_filename, 'w')
    destination_file.write(get_process_line(content))
    destination_file.write("\tsequence seq0 {\n")
    for i, unit in enumerate(units):
        destination_file.write(unit)

    destination_file.write("\t\titeration iter0 {\n")
    for i, unit in enumerate(units):
        for j, identifier in enumerate(IDENTIFIERS):
            if identifier in unit:
                identifier_index = unit.index(identifier)
                opening_bracket_index = unit.index(OPENING_BRACKET)
                m.update(str(i))
                unit_body = unit[opening_bracket_index + len(OPENING_BRACKET) + 1:]
                unit = "\t" + unit[:identifier_index + len(
                    identifier)] + " " + "a" + m.hexdigest() + " " + OPENING_BRACKET + "\n\t" + unit_body.replace("\n",
                                                                                                            "\n\t",
                                                                                                            unit_body.count(
                                                                                                                "\n") - 1)
                break
        destination_file.write(unit)

    destination_file.write("\t\t}\n")
    destination_file.write("\t}\n")
    destination_file.write("}")
    destination_file.close()

    open(origin_filename, 'w').close()
    origin_filename = open(origin_filename, 'w')
    branch_check = 0

    with open(destination_filename) as f:
        for line in f:
            if branch_check is 0:
                origin_filename.write(line)
                if "branch" in line:
                    branch_check = 1
            else:
                if "branch" not in line:
                    branch_check = 0
                    origin_filename.write(line)
    origin_filename.close()
    process = subprocess.Popen(BASH_COMMAND.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]


def pml_tx_remove_selections(origin_filename):
    with open(origin_filename) as f:
        content = f.readlines()

    SEQUENCE_IDENTIFIER = "sequence"
    ITERATION_IDENTIFIER = "iteration"
    BRANCH_IDENTIFIER = "branch"
    ACTION_IDENTIFIER = "action"
    PROCESS_IDENTIFIER = "process"
    SELECTION_IDENTIFIER = "selection"
    LESS_IDENTIFIER = "/*less"

    IDENTIFIERS = [
        SELECTION_IDENTIFIER,
        SEQUENCE_IDENTIFIER,
        BRANCH_IDENTIFIER,
        ACTION_IDENTIFIER,
        PROCESS_IDENTIFIER,
    ]

    OPENING_BRACKET = "{"
    CLOSING_BRACKET = "}"

    OPENING_SQUARE_BRACKET = "["

    units = []
    removal_units = []

    def get_components(components):
        units = []
        unit = ""
        non_selection_structure_open = False
        for i, line in enumerate(components):
            line_stripped = "".join(line.split())
            if non_selection_structure_open and line_stripped == CLOSING_BRACKET:
                unit += line
                units.append(unit)
                non_selection_structure_open = False
                unit = ""
            elif ((SELECTION_IDENTIFIER not in line) and (
                        LESS_IDENTIFIER not in line) and not non_selection_structure_open):
                unit += line
                non_selection_structure_open = True
            elif LESS_IDENTIFIER not in line and non_selection_structure_open:
                unit += line

            if LESS_IDENTIFIER in line:
                break
        return units

    filtered_lines = []
    selection_identifier_open = False
    for i, line in enumerate(content):
        if SELECTION_IDENTIFIER in line:
            selection_identifier_open = True
        if selection_identifier_open and OPENING_BRACKET in line:
            filtered_lines = content[i + 1:]
            break

    source_units = get_components(filtered_lines)

    less_identifier_open = False
    less_lines = []
    for i, line in enumerate(content):
        if LESS_IDENTIFIER in line:
            less_identifier_open = True
        if less_identifier_open and OPENING_SQUARE_BRACKET in line:
            index_after_opening_square_bracket = line.index(OPENING_SQUARE_BRACKET)
            line = line[index_after_opening_square_bracket + len(OPENING_SQUARE_BRACKET):]
            content[i] = line
            less_lines = content[i:]
            break

    less_units = get_components(less_lines)
    removal_identifiers = []

    for i in range(len(less_units)):
        less_unit = less_units[i]
        for j, identifier in enumerate(IDENTIFIERS):
            if identifier in less_unit:
                action_and_id = less_unit[:less_unit.index(OPENING_BRACKET)].strip()
                removal_identifiers.append(action_and_id)

    filtered_units = []

    for i, source_unit in enumerate(source_units):
        skip = False
        for j, removal_identifier in enumerate(removal_identifiers):
            if removal_identifier in source_unit:
                skip = True
                break
        if not skip:
            filtered_units.append(source_unit)

    origin_filename = open(origin_filename, 'w')
    origin_filename.write("selection seq0 {\n")
    for i, unit in enumerate(filtered_units):
        origin_filename.write(unit)


def pml_tx_serialize_branch_naive(origin_filename):
    with open(origin_filename) as f:
        content = f.readlines()

    queue = []
    for i, line in enumerate(content):
        queue.append(line)

    SEQUENCE_IDENTIFIER = "sequence"
    BRANCH_IDENTIFIER = "branch"

    origin_filename = open(origin_filename, 'w')

    for i in range(len(queue)):
        line = queue[i]

        if BRANCH_IDENTIFIER in line:
            start_index = line.index(BRANCH_IDENTIFIER)
            origin_filename.write(
                line[:start_index] + SEQUENCE_IDENTIFIER + line[(start_index + len(BRANCH_IDENTIFIER)):])
        else:
            origin_filename.write(line)

    f.close()


def pml_tx_serialize_branch_2_way(origin_filename):
    m = hashlib.md5()
    with open(origin_filename) as f:
        content = f.readlines()

    SEQUENCE_IDENTIFIER = "sequence"
    BRANCH_IDENTIFIER = "branch"
    ACTION_IDENTIFIER = "action"
    PROCESS_IDENTIFIER = "process"
    SELECTION_IDENTIFIER = "selection"

    OPENING_BRACKET = "{"
    CLOSING_BRACKET = "}"

    with open(origin_filename) as f:
        string_content = f.read()
        if BRANCH_IDENTIFIER not in string_content:
            return False

    action_structure_prefix = ""
    meta_opening_body = []
    meta_closing_body = []
    action_identifier_open = False
    contains_branch_identifier = False

    units = []
    origin_filename = open(origin_filename, 'w')
    unit = ""
    for i, line in enumerate(content):
        line_stripped = "".join(line.split())
        # now, we want to obtain branches
        if BRANCH_IDENTIFIER in line:
            sequence_identifier_open = True
            contains_branch_identifier = True
            start_index = line.index(BRANCH_IDENTIFIER)
            meta_opening_body.append(
                line[:start_index] + SELECTION_IDENTIFIER + line[(start_index + len(BRANCH_IDENTIFIER)):])
        elif ACTION_IDENTIFIER in line and contains_branch_identifier:
            action_identifier_open = True
            action_structure_prefix = line[:line.index(ACTION_IDENTIFIER)]
            m.update(str(time.time()))
            line = ACTION_IDENTIFIER + " " + "PLACEHOLDER" + " " + OPENING_BRACKET + "\n"
            unit += action_structure_prefix + "\t" + line
        elif line_stripped == CLOSING_BRACKET and action_identifier_open:
            action_identifier_open = False
            unit += action_structure_prefix + "\t" + line
            units.append(unit)
            unit = ""
        elif action_identifier_open:
            unit += action_structure_prefix + "\t" + line
        elif PROCESS_IDENTIFIER in line:
            meta_opening_body.append(line)
        elif line_stripped == CLOSING_BRACKET and contains_branch_identifier:
            meta_closing_body.append(line)
    number_of_ways = 2
    for i, line in enumerate(meta_opening_body):
        origin_filename.write(line)
    for i in range(number_of_ways):
        origin_filename.write(action_structure_prefix + ('sequence s%s {\n' % (i)))
        for i, unit in enumerate(units):
            m.update(str(time.time()))
            temp = "a" + m.hexdigest()
            unit = unit.replace("PLACEHOLDER", temp)
            origin_filename.write(unit)
        origin_filename.write(action_structure_prefix + '}\n')
        units = units[::-1]
    for i, line in enumerate(meta_closing_body):
        origin_filename.write(line)
    f.close()


def sequence_flatten(origin_filename):
    with open(origin_filename) as f:
        content = f.readlines()

    queue = []
    for i, line in enumerate(content):
        queue.append(line)

    PROCESS_IDENTIFIER = "process"
    SEQUENCE_IDENTIFIER = "sequence"
    ACTION_IDENTIFIER = "action"
    CLOSING_BRACKET = "}"

    inner_sequence_found = False
    outer_sequence_found = False
    outstanding_action = False

    origin_filename = open(origin_filename, 'w')

    for i in range(len(queue)):
        line = queue[i]
        line_stripped = "".join(line.split())

        if PROCESS_IDENTIFIER in line:
            origin_filename.write(line)
        elif SEQUENCE_IDENTIFIER in line and not (outer_sequence_found):
            origin_filename.write(line)
            outer_sequence_found = True
        elif SEQUENCE_IDENTIFIER in line and outer_sequence_found:
            inner_sequence_found = True
        elif ACTION_IDENTIFIER in line:
            origin_filename.write(line)
            outstanding_action = True
        elif inner_sequence_found and not (outstanding_action) and line_stripped == CLOSING_BRACKET:
            inner_sequence_found = False
        elif outstanding_action and line_stripped == CLOSING_BRACKET:
            origin_filename.write(line)
            outstanding_action = False
        else:
            origin_filename.write(line)
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


@app.route('/tx-parallelize-sequence', methods=['GET'])
def tx_parallelize_sequence():
    db = mongo.db.dist
    db.parsequence.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        pml_tx_parallelize_sequence(path)

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    db.parsequence.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})

    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ pml_tx_parallelize_sequence ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('parallelizesequence.html', par_sequence=db.parsequence.find())


@app.route('/tx-remove-selections', methods=['GET'])
def tx_remove_selections():
    db = mongo.db.dist
    db.removeselections.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        pml_tx_remove_selections(path)

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    db.removeselections.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})

    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ pml_tx_remove_selections ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('removeselections.html', remove_selections=db.removeselections.find())


@app.route('/tx-unroll-iteration', methods=['GET'])
def tx_unroll_iteration():
    db = mongo.db.dist
    db.unrolliteration.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        pml_tx_unroll_iteration(path)

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    db.unrolliteration.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})

    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ pml_tx_unroll_iteration ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('unrolliteration.html', unroll_iteration=db.unrolliteration.find())


@app.route('/tx-serialize-branch-naive', methods=['GET'])
def tx_serialize_branch_naive():
    db = mongo.db.dist
    db.serializebranchnaive.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        pml_tx_serialize_branch_naive(path)

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    db.serializebranchnaive.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})

    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ pml_tx_serialize_branch_naive ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('serializebrnaive.html', s_b_naive=db.serializebranchnaive.find())


@app.route('/tx-serialize-branch-2-way', methods=['GET'])
def tx_serialize_branch_2_way():
    db = mongo.db.dist
    db.serializebranchtwoway.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        pml_tx_serialize_branch_2_way(path)

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    db.serializebranchtwoway.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})

    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ pml_tx_serialize_branch_2_way ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('serializebrtwoway.html', s_b_two_way=db.serializebranchtwoway.find())


@app.route('/tx-sequence-flatten', methods=['GET'])
def tx_sequence_flatten():
    db = mongo.db.dist
    db.sequenceflatten.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        sequence_flatten(path)

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    # for l in line_list:
    #     print(l)
    #     if "process" or "task" or "sequence" or "branch" or "selection" or "iteration" in l:
    #         print(l.count(' '))
    db.sequenceflatten.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})
    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ sequence_flatten ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('sequenceflatten.html', seq_flatten=db.sequenceflatten.find())


@app.route('/select-transformation-type', methods=['GET'])
def select_tx_type():
    return render_template('transformationselection.html')


@app.route('/analyse-files', methods=['POST'])
def analyse_selected_files():
    db = mongo.db.dist
    db.analysis.drop()
    files = db.check.find()
    m = md5.new()
    BASH_COMMAND = "./peos/pml/drugfinder/drugFind "
    bash_output = "cat drug_list.txt"

    for file in files:
        path = file['path']
        file_path = path
        name = file['name']

        # f = open(file_path, "r")
        # lines = f.readlines()
        # f.close()
        #
        # f = open(file_path, "w")
        # for line in lines:
        #     if "branch" in line:
        #         line
        #         # add branch name to variable and export for use as name with parallel ddi
        # f.close()

        m.update(name)
        execute_command = BASH_COMMAND + path
        subprocess.Popen(execute_command.split(), stdout=subprocess.PIPE)
        process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        log_process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        check_process = subprocess.Popen(bash_output.split(), stdout=subprocess.PIPE)
        error_process = subprocess.Popen(bash_output.split(), stderr=subprocess.PIPE)
        log_error_process = subprocess.Popen(bash_output.split(), stderr=subprocess.PIPE)

        if check_process.communicate()[0] != "":
            output = process.communicate()[0]

            # identify the parallel DDIs here
            parallel_count = output.count("[")
            if parallel_count > 1:
                sep_1 = "]"
                output_sep_1 = output.split(sep_1, 1)[0]
                output_sep_final = output_sep_1 + ","
                output_sep_1 += sep_1
                output_remainder = (output[output.index(output_sep_1) + len(output_sep_1):]).strip()
                output_remainder = output_remainder.replace('\n', '')
                output_remainder = output_remainder.replace('"', '')
                output_remainder = output_remainder.replace('[', '')
                final_string = output_sep_final + output_remainder
                final_string = final_string.replace('"', '')
                db.analysis.insert(
                    {'name': name, 'path': path, 'process': final_string, 'id': m.hexdigest()})
                rootLogger.info('\n')
                rootLogger.info("Name = [ " + name + " ]")
                rootLogger.info("Path = [ " + path + " ]")
                rootLogger.info(log_process.communicate()[0])
                return render_template('analyse.html', analyse_files=db.analysis.find())

            # continue here if no parallel DDIs exist
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
    db.sequenceflatten.drop()
    db.serializebranchnaive.drop()
    db.serializebranchtwoway.drop()
    db.unrolliteration.drop()
    db.removeselections.drop()
    db.parsequence.drop()

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
