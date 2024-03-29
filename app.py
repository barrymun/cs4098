# Python 2.7 required
# Use "source venv/bin/activate"

import hashlib
import logging
import md5
import os
import re
import subprocess
import random
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

    drug_list = re.sub('[(]', '', drug_list)
    drug_list = re.sub('[)]', '', drug_list)
    drug_list = re.sub('[[]', '', drug_list)
    drug_list = re.sub('[]]', '', drug_list)
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
                        print(line)
                        line_to_list = line.split(",")
                        display.append(line_to_list)
                    count += 1
            count = 1

    display_count = 0
    for d_list in display:
        for val in d_list:
            if display_count > 4:
                break
            if display_count is 0:
                val = "Drug 1 = [ " + val + " ]"
                d_list[display_count] = val
            if display_count is 1:
                val = "Drug 2 = [ " + val + " ]"
                d_list[display_count] = val
            if display_count is 2:
                val = "Interaction type between these drugs = [ " + val + " ]"
                d_list[display_count] = val
            if display_count is 3:
                val = "Timing between ingestion = [ " + val + " ]"
                d_list[display_count] = val
            if display_count is 4:
                val = "Unit of timing measurement = [ " + val + " ]"
                d_list[display_count] = val
            display_count += 1

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

def get_names_for_identifier_in_line(identifier, line):
    """
    branch branch_name {
    """
    if (identifier not in line):
        return None

    identifier_start_index = line.index(identifier)
    identifier_end_index = identifier_start_index + len(identifier)

    if "{" not in line:
        return None
    opening_curly_brace_index = line.index("{", identifier_end_index)

    identifier_name = line[identifier_end_index:opening_curly_brace_index].strip()
    return identifier_name

def generate_unique_name(identifier, existing_names):
    random_number = str(random.randint(0,100000))
    if identifier not in existing_names:
        return identifier + "_" + random_number

    identifier_names = existing_names[identifier]
    is_name_generated = False
    return_identifier_name = None
    while not(is_name_generated):
        for i, identifier_name in enumerate(identifier_names):
            return_identifier_name = identifier_name + "_" + random_number
            if not(return_identifier_name in identifier_names):
                is_name_generated = True
                break

    return return_identifier_name


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

    existing_names = {}
    for i, identifier in enumerate(IDENTIFIERS):
        for j, line in enumerate(content):
            name = get_names_for_identifier_in_line(identifier, line)
            if not name:
                continue
            if identifier not in existing_names:
                existing_names[identifier] = []

            existing_names[identifier].append(name)

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
                selection_identifier_name = generate_unique_name(SELECTION_IDENTIFIER, existing_names)

                if not(SELECTION_IDENTIFIER in existing_names):
                    existing_names[SELECTION_IDENTIFIER] = []

                existing_names[SELECTION_IDENTIFIER].append(selection_identifier_name)
                line = line[:identifier_end_index] + " " + selection_identifier_name + " " + "{\n"
                unit += line
                non_meta_structure_open = True
            elif (BRANCH_IDENTIFIER in line and not non_meta_structure_open):
                identifier_start_index = line.index(BRANCH_IDENTIFIER)
                identifier_end_index = identifier_start_index + len(BRANCH_IDENTIFIER)
                branch_identifier_name = generate_unique_name(BRANCH_IDENTIFIER, existing_names)
                existing_names[BRANCH_IDENTIFIER].append(branch_identifier_name)

                if not(BRANCH_IDENTIFIER in existing_names):
                    existing_names[BRANCH_IDENTIFIER] = []

                line = line[:identifier_end_index] + " " + branch_identifier_name + " " + "{\n"
                unit += line
                non_meta_structure_open = True
            elif (ACTION_IDENTIFIER in line and not non_meta_structure_open):
                identifier_start_index = line.index(ACTION_IDENTIFIER)
                identifier_end_index = identifier_start_index + len(ACTION_IDENTIFIER)
                action_identifier_name = generate_unique_name(ACTION_IDENTIFIER, existing_names)
                existing_names[ACTION_IDENTIFIER].append(action_identifier_name)

                if not(ACTION_IDENTIFIER in existing_names):
                    existing_names[ACTION_IDENTIFIER] = []

                line = line[:identifier_end_index] + " " + action_identifier_name + " " + "{\n"
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

    branch_identifier_name = generate_unique_name(BRANCH_IDENTIFIER, existing_names)
    if not (BRANCH_IDENTIFIER in existing_names):
        existing_names[BRANCH_IDENTIFIER] = []
    existing_names[BRANCH_IDENTIFIER].append(branch_identifier_name)


    destination_resource.write("\tbranch %s {\n" % branch_identifier_name)

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
        ITERATION_IDENTIFIER,
    ]

    existing_names = {}
    for i, identifier in enumerate(IDENTIFIERS):
        for j, line in enumerate(content):
            name = get_names_for_identifier_in_line(identifier, line)
            if not name:
                continue
            if identifier not in existing_names:
                existing_names[identifier] = []

            existing_names[identifier].append(name)

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

            selection_identifier_name = generate_unique_name(SELECTION_IDENTIFIER, existing_names)

            if not (SELECTION_IDENTIFIER in existing_names):
                existing_names[SELECTION_IDENTIFIER] = []

            existing_names[SELECTION_IDENTIFIER].append(selection_identifier_name)

            line = line[:identifier_end_index] + " " + selection_identifier_name + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif (BRANCH_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(BRANCH_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(BRANCH_IDENTIFIER)
            branch_identifier_name = generate_unique_name(BRANCH_IDENTIFIER, existing_names)

            if not (BRANCH_IDENTIFIER in existing_names):
                existing_names[BRANCH_IDENTIFIER] = []

            existing_names[BRANCH_IDENTIFIER].append(branch_identifier_name)

            line = line[:identifier_end_index] + " " + branch_identifier_name + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif (ACTION_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(ACTION_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(ACTION_IDENTIFIER)

            action_identifier_name = generate_unique_name(ACTION_IDENTIFIER, existing_names)

            if not (ACTION_IDENTIFIER in existing_names):
                existing_names[ACTION_IDENTIFIER] = []

            existing_names[ACTION_IDENTIFIER].append(action_identifier_name)

            line = line[:identifier_end_index] + " " + action_identifier_name + " " + "{\n"
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

    iteration_name = existing_names[ITERATION_IDENTIFIER][0]

    destination_file.write("\t\titeration " + iteration_name + " {\n")
    for i, unit in enumerate(units):
        for j, identifier in enumerate(IDENTIFIERS):
            if identifier in unit:
                identifier_index = unit.index(identifier)
                opening_bracket_index = unit.index(OPENING_BRACKET)
                m.update(str(i))
                unit_body = unit[opening_bracket_index + len(OPENING_BRACKET) + 1:]
                generated_name = generate_unique_name(identifier, existing_names)
                if not(identifier in existing_names):
                    existing_names[identifier] = []
                existing_names[identifier].append(generated_name)
                unit = "\t" + unit[:identifier_index + len(
                    identifier)] + " " + "a" + generated_name + " " + OPENING_BRACKET + "\n\t" + unit_body.replace("\n",
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
    BASH_COMMAND = "rm less_destination.pml"
    destination_filename = "less_destination.pml"

    with open(origin_filename) as f:
        content_lines = f.readlines()

    with open(origin_filename) as f:
        content_string = f.read()

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
        ITERATION_IDENTIFIER,
    ]

    existing_names = {}
    for i, identifier in enumerate(IDENTIFIERS):
        for j, line in enumerate(content_lines):
            name = get_names_for_identifier_in_line(identifier, line)
            if not name:
                continue
            if identifier not in existing_names:
                existing_names[identifier] = []

            existing_names[identifier].append(name)


    OPENING_BRACKET = "{"
    CLOSING_BRACKET = "}"

    OPENING_SQUARE_BRACKET = "["
    CLOSING_SQUARE_BRACKET = "]"

    WHITESPACE = " "
    EMPTY_SPACE = ""
    less_sequence_args = ""

    less_identifier_index_start = -1
    if LESS_IDENTIFIER in content_string:
        less_identifier_index_start = content_string.index(LESS_IDENTIFIER)
        less_args_start_index = content_string.index(OPENING_SQUARE_BRACKET, less_identifier_index_start)
        less_args_end_index = content_string.index(CLOSING_SQUARE_BRACKET, less_args_start_index)

        less_sequence_args = content_string[less_args_start_index + 1:less_args_end_index]
        less_sequence_args = less_sequence_args.replace(WHITESPACE, EMPTY_SPACE)
        less_sequence_args = less_sequence_args.split(",")

    process_identifier_open = False
    sequence_identifier_open = False
    non_process_identifier_open = False
    line_identifier_match = False

    sequence_body_groups = []
    current_sequence_group = ""
    for i, line in enumerate(content_lines):
        if PROCESS_IDENTIFIER in line:
            process_identifier_open = True
            continue
        if SEQUENCE_IDENTIFIER in line:
            sequence_identifier_open = True
        else:
            line_identifier_match = False
            for j, identifier in enumerate(IDENTIFIERS):
                if identifier in line:
                    non_process_identifier_open = True
                    line_identifier_match = True
                    current_sequence_group += line

            if non_process_identifier_open and (CLOSING_BRACKET in line) and (OPENING_BRACKET not in line):
                current_sequence_group += line
                non_process_identifier_open = False
                sequence_body_groups.append(current_sequence_group)
                current_sequence_group = ""
            elif not (line_identifier_match):
                current_sequence_group += line

    less_sequences = []
    for k, sequence_body in enumerate(sequence_body_groups):
        match = False
        for i, less_sequence in enumerate(less_sequence_args):
            if less_sequence in sequence_body:
                match = True
                break
        if not (match):
            less_sequences.append(sequence_body)

    def get_process_line(content):
        for i, line in enumerate(content):
            if PROCESS_IDENTIFIER in line:
                break
        return line

    def get_sequenece_line(content):
        for i, line in enumerate(content):
            if SEQUENCE_IDENTIFIER in line:
                break
        return line

    destination_file = open(destination_filename, 'w')
    destination_file.write(get_process_line(content_lines))
    destination_file.write(get_sequenece_line(content_lines))
    for i, unit in enumerate(less_sequences):
        destination_file.write(unit)

    get_sequence_ident = get_sequenece_line(content_lines)[
                         0:get_sequenece_line(content_lines).index(SEQUENCE_IDENTIFIER)]

    destination_file.write(get_sequence_ident + CLOSING_BRACKET + "\n")
    destination_file.write("}")
    destination_file.close()

    open(origin_filename, 'w').close()
    origin_filename = open(origin_filename, 'w')

    with open(destination_filename) as f:
        for line in f:
            origin_filename.write(line)
    origin_filename.close()

    process = subprocess.Popen(BASH_COMMAND.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]


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
        content_lines = f.readlines()

    SEQUENCE_IDENTIFIER = "sequence"
    BRANCH_IDENTIFIER = "branch"
    ACTION_IDENTIFIER = "action"
    PROCESS_IDENTIFIER = "process"
    SELECTION_IDENTIFIER = "selection"
    ITERATION_IDENTIFIER = "iteration"

    IDENTIFIERS = [
        SELECTION_IDENTIFIER,
        SEQUENCE_IDENTIFIER,
        BRANCH_IDENTIFIER,
        ACTION_IDENTIFIER,
        PROCESS_IDENTIFIER,
        ITERATION_IDENTIFIER
    ]

    existing_names = {}
    for i, identifier in enumerate(IDENTIFIERS):
        for j, line in enumerate(content_lines):
            name = get_names_for_identifier_in_line(identifier, line)
            if not name:
                continue
            if identifier not in existing_names:
                existing_names[identifier] = []

            existing_names[identifier].append(name)

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
    for i, line in enumerate(content_lines):
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
            action_identifier_name = generate_unique_name(ACTION_IDENTIFIER, existing_names)

            if not (ACTION_IDENTIFIER in existing_names):
                existing_names[ACTION_IDENTIFIER] = []

            existing_names[ACTION_IDENTIFIER].append(action_identifier_name)


            unit = unit.replace("PLACEHOLDER", action_identifier_name)
            origin_filename.write(unit)
        origin_filename.write(action_structure_prefix + '}\n')
        units = units[::-1]
    for i, line in enumerate(meta_closing_body):
        origin_filename.write(line)
    f.close()


def reorder_sequence(origin_filename):
    BASH_COMMAND = "rm reorder_destination.pml"
    destination_filename = "reorder_destination.pml"

    with open(origin_filename) as f:
        content_lines = f.readlines()

    with open(origin_filename) as f:
        content_string = f.read()

    SEQUENCE_IDENTIFIER = "sequence"
    ITERATION_IDENTIFIER = "iteration"
    BRANCH_IDENTIFIER = "branch"
    ACTION_IDENTIFIER = "action"
    PROCESS_IDENTIFIER = "process"
    SELECTION_IDENTIFIER = "selection"

    REORDER_IDENTIFIER = "/*reorder"

    IDENTIFIERS = [
        SELECTION_IDENTIFIER,
        SEQUENCE_IDENTIFIER,
        BRANCH_IDENTIFIER,
        ACTION_IDENTIFIER,
        PROCESS_IDENTIFIER,
        ITERATION_IDENTIFIER
    ]

    existing_names = {}
    for i, identifier in enumerate(IDENTIFIERS):
        for j, line in enumerate(content_lines):
            name = get_names_for_identifier_in_line(identifier, line)
            if not name:
                continue
            if identifier not in existing_names:
                existing_names[identifier] = []

            existing_names[identifier].append(name)

    OPENING_BRACKET = "{"
    CLOSING_BRACKET = "}"

    OPENING_SQUARE_BRACKET = "["
    CLOSING_SQUARE_BRACKET = "]"

    WHITESPACE = " "
    EMPTY_SPACE = ""

    reorder_identifier_index_start = -1
    if REORDER_IDENTIFIER in content_string:
        reorder_identifier_index_start = content_string.index(REORDER_IDENTIFIER)
        reorder_args_start_index = content_string.index(OPENING_SQUARE_BRACKET, reorder_identifier_index_start)
        reorder_args_end_index = content_string.index(CLOSING_SQUARE_BRACKET, reorder_args_start_index)

        reorder_sequence_args = content_string[reorder_args_start_index + 1:reorder_args_end_index]
        reorder_sequence_args = reorder_sequence_args.replace(WHITESPACE, EMPTY_SPACE)
        reorder_sequence_args = reorder_sequence_args.split(",")
    else:
        return False
    reorder_sequence_args = map(int, reorder_sequence_args)

    process_identifier_open = False
    sequence_identifier_open = False
    non_process_identifier_open = False
    line_identifier_match = False

    sequence_body_groups = []
    current_sequence_group = ""
    for i, line in enumerate(content_lines):
        if PROCESS_IDENTIFIER in line:
            process_identifier_open = True
            continue
        if SEQUENCE_IDENTIFIER in line:
            sequence_identifier_open = True
        else:
            line_identifier_match = False
            for j, identifier in enumerate(IDENTIFIERS):
                if identifier in line:
                    non_process_identifier_open = True
                    line_identifier_match = True
                    current_sequence_group += line

            if non_process_identifier_open and (CLOSING_BRACKET in line) and (OPENING_BRACKET not in line):
                current_sequence_group += line
                non_process_identifier_open = False
                sequence_body_groups.append(current_sequence_group)
                current_sequence_group = ""
            elif not (line_identifier_match):
                current_sequence_group += line

    reordered_sequences = []
    for i, j in enumerate(reorder_sequence_args):
        reordered_sequences.append(sequence_body_groups[j])

    def get_process_line(content):
        for i, line in enumerate(content):
            if PROCESS_IDENTIFIER in line:
                break
        return line

    def get_sequenece_line(content):
        for i, line in enumerate(content):
            if SEQUENCE_IDENTIFIER in line:
                break
        return line

    destination_file = open(destination_filename, 'w')
    destination_file.write(get_process_line(content_lines))
    destination_file.write(get_sequenece_line(content_lines))
    for i, unit in enumerate(sequence_body_groups):
        destination_file.write(unit)

    get_sequence_ident = get_sequenece_line(content_lines)[
                         0:get_sequenece_line(content_lines).index(SEQUENCE_IDENTIFIER)]

    destination_file.write(get_sequence_ident + CLOSING_BRACKET + "\n")
    destination_file.write("}")
    destination_file.close()

    open(origin_filename, 'w').close()
    origin_filename = open(origin_filename, 'w')

    with open(destination_filename) as f:
        for line in f:
            origin_filename.write(line)
    origin_filename.close()
    process = subprocess.Popen(BASH_COMMAND.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    return True


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


@app.route('/tx-reorder-sequence', methods=['GET'])
def tx_reorder_sequence():
    db = mongo.db.dist
    db.reordersequence.drop()
    BASH_COMMAND = "cat "
    name = ""
    path = ""
    m = md5.new()

    action_response = False
    for file in db.selected.find():
        name = file['name']
        m.update(name)
        path = file['path']
        action_response = reorder_sequence(path)

    if not(action_response):
        return render_template('cannot-perform-action.html')

    executeCommand = BASH_COMMAND + path
    process = subprocess.Popen(executeCommand.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    sep = "\n"
    line_list = output.split(sep)
    # for l in line_list:
    #     print(l)
    #     if "process" or "task" or "sequence" or "branch" or "selection" or "iteration" in l:
    #         print(l.count(' '))
    db.reordersequence.insert({'name': name, 'path': path, 'process': line_list, 'id': m.hexdigest()})
    rootLogger.info('\n')
    rootLogger.info("Name = [ " + name + " ]")
    rootLogger.info("Path = [ " + path + " ]")
    rootLogger.info("Action = [ reorder sequence ]")
    rootLogger.info("Process = [ " + str(output) + " ]")
    return render_template('reordersequence.html', reorder_seq=db.reordersequence.find())


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
    ext = extension
    alphabetical_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(ext)):
                file_path = os.path.join(root, file)
                if ((file, file_path) in alphabetical_list):
                    continue
                # search Mongo. If in Mongo, ignore. Otherwise, add.
                alphabetical_list.append((file, file_path))

    alphabetical_list.sort()
    for f, fp in alphabetical_list:
        m = md5.new()
        m.update(f)
        db.files.insert({'name': f, 'path': fp, 'id': m.hexdigest()})


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
    db.reordersequence.drop()
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
