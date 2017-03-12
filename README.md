# Overwatch

# Setup Guide

### Group Members:
Aaron Joyce
<br/>
Bryan Quirke
<br/>
Erik Eviston
<br/>
Jessa Pajarito
<br/>
Neil Barry-Murphy

# Using the Flask Application

Activate the virtual environment (Python 2.7 required):
```bash
source venv/bin/activate
```
Run the setup script (First time setup following initial clone - required only once):
```bash
bash setup.sh
```
Restart mongo:
```bash
sudo service mongod restart
```
Run the flask application:
```python
python app.py
```
(If The Flask Application Fails)
<br/>
Install necessary requirements with root permissions and restart mongo:
```bash
sudo pip install -r requirements.txt

sudo service mongod restart
```
Now, re-start the application:
```python
python app.py
```
Navigate to the homepage:
```bash
http://127.0.0.1:5000/
```

# Logging

Open another terminal in the same directory and execute the following:
<br/>
Activate the virtual environment:
```bash
source venv/bin/activate
```

Once the app has been started on the previous terminal: - (PML and DINTO Log-file Generation)
```bash
tail -f info.log
```

# In-Depth Testing
Please note that all explanations are accompanied by images.
<br/>
See the `documentation/testing/testing-process` section of this repo for more information.

## Successful Tests

- Navigate to the homepage (process described above).
- Select "Begin Analysis".
- Select a pml file (`depression.pml` or `irritable_bowel_syndrome.pml`). - (PML file selection)
- `depression.pml` describes only one drug, and will list all interactions of that drug.
- `irritable_bowel_syndrome.pml` describes multiple (2) drugs, and will list the interactions between these 2 drugs. - (PML File Loading)
- When a file has been selected, click "Check Validity of Selected File" to continue.
- The next page displayed is the results of a pml file check. - (Running PML Analysis)
- The result will be either valid or invalid. An invalid result will not allow for progression.
- If result is valid, click "Analyse File" to extract the drug information. - (On-Screen PML Reporting)
- You will now be presented with a list containing drug information realting to the title of the pml. (ie - depression will yield a prescription of fluoxetine)
- Click "Search DINTO for Interactions" to continue.
- Next, select the DINTO knowledge base. For the purposes of this test, the only KB is "test_selection.owl". - (Select specific OWL Ontology)
- Select the file, and click "Load Knowledge Base" to continue. - (Load Selected Ontology)
- A list of drug-drug interactions will now be displayed on screen. - (On-Screen DINTO Reporting)
- Click the available links to view drug references for single-instance drug interactions.
- Select "Finished" when analysis is complete. You will be redirected to the homepage.

## Unsuccessful Tests

- Navigate to the homepage (process described above).
- Select "Begin Analysis".
- Select a pml file (`pml_format_error.pml`, `pml_format_correct_analysis_error.pml` or `pml_format_correct_analysis_correct_no_drug_links.pml`).
- `pml_format_error.pml` has a syntax error in the file. The system will highlight this.
- `pml_format_correct_analysis_error.pml` describes a pml file that syntactically correct, but the analysis fails as no drug mentions are found. The system will also highlight this.
- `pml_format_correct_analysis_correct_no_drug_links.pml` describes a test that has a syntactically correct pml file, yields drug or drug names from the analysis, but no links exist in DINTO for these referenced drugs. This test result will again be highlighted by the system.
- The following instructions are the same as above, but various descriptive error messages will be encountered.
- When a file has been selected, click "Check Validity of Selected File" to continue.
- The next page displayed is the results of a pml file check.
- The result will be either valid or invalid. An invalid result will not allow for progression. - (PML Error and Warning highlights)
- If result is valid, click "Analyse File" to extract the drug information.
- You will now be presented with a list containing drug information relating to the title of the pml. (ie - depression will yield a prescription of fluoxetine)
- Click "Search DINTO for Interactions" to continue.
- Next, select the DINTO knowledge base. For the purposes of this test, the only KB is "test_selection.owl".
- Select the file, and click "Load Knowledge Base" to continue.
- If errors exist from any previous section, the relevant DINTO (or PML if previous) errors will be highlighted by the system. - (DINTO Error and Warning highlights)
- Select "Finished" when analysis is complete. You will be redirected to the homepage.

# Using the Mongo Database
Installation for Ubuntu 16.04 will be handled by the setup script.
<br/>
Open a new terminal and execute the following:
<br/><br/>
Log In to the Mongo shell:
```bash
mongo
```
Switch to the project database:
```mongo
use app
```
List all currently available collections:
<br/>
(Should be empty prior to launching the flask app)
```mongo
db.getCollectionNames()
```
List all pml files in the project, for example:
```mongo
db.dist.files.find()
```
List all pml files that you have selected as a user:
```mongo
db.dist.selected.find()
```
List all pml files that have been analysed:
```mongo
db.dist.analysis.find()
```

## Deactivating the Virtual Environment

When finished with analysis of the system, execute:
```bash
deactivate
```
This will disable the virtual environment.
