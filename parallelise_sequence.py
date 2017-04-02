import hashlib
import time

origin_filename = "parallelise_origin.pml"
destination_filename = "parallelise_destination.pml"

destination_resource = open(destination_filename, 'w')

with open(origin_filename) as f:
    content = f.readlines()


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
            line = line[:identifier_end_index] + " " + m.hexdigest() + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif (BRANCH_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(BRANCH_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(BRANCH_IDENTIFIER)
            line = line[:identifier_end_index] + " " + m.hexdigest() + " " + "{\n"
            unit += line
            non_meta_structure_open = True
        elif (ACTION_IDENTIFIER in line and not non_meta_structure_open):
            identifier_start_index = line.index(ACTION_IDENTIFIER)
            identifier_end_index = identifier_start_index + len(ACTION_IDENTIFIER)
            line = line[:identifier_end_index] + " " + m.hexdigest() + " " + "{\n"
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
destination_resource.write("\tbranch %s {\n" % m.hexdigest())

for i, j in enumerate(units):
    destination_resource.write(j)

destination_resource.write("\t}\n")
destination_resource.write("}")