# Python 2.7 required
# Use "source venv/bin/activate"

from flask import Flask, Markup, render_template
from Tkinter import Tk
from tkFileDialog import askopenfilename

import webbrowser
import os

app = Flask(__name__)


@app.route('/')
def search_path():
    path = os.getcwd() + "/peos"
    #print path
    return render_template('index.html', pml_files=get_pml(path))


# def get_pml(path):
#     pml_files = []
#     for root, dirs, files in os.walk(path):
#         for current_directory in dirs:
#             for currentFile in files:
#                 ext = ('.pml')
#                 if currentFile.endswith(ext):
#                     pml_files.append(root + "/" + current_directory + "/" + currentFile)
#     return pml_files


def get_pml(path):
    pml_files = []
    ext = ('.pml')
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                #print (os.path.join(root, file))
                pml_files.append(os.path.join(root, file))
    return pml_files


# @app.route('/')
# def index():
#     # we don't want a full GUI, so keep the root window from appearing
#     Tk().withdraw()
#     # show an "Open" dialog box and return the path to the selected file
#     filename = askopenfilename()
#     # Return content of this file itself
#     this_source = open(filename).read()
#     return "<pre>%s</pre>" % Markup.escape(this_source)


# <title>Path: {{ tree.name }}</title>
# <h1>{{ tree.name }}</h1>
# <ul>
#     {%- for item in tree.children recursive %}
#     <li>{{ item.name }}
#         {%- if item.children -%}
#         <ul>{{ loop(item.children) }}</ul>
#         {%- endif %}
#     </li>
#     {%- endfor %}
# </ul>

if __name__ == '__main__':
    app.run()
