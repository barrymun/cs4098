# Overwatch

## Status: ![build passing](https://raw.githubusercontent.com/barrymun/cs4098/master/static/images/build-passing.png?token=AO6TcMUE6BKKgsIL7hMMzsMszlS9E7ILks5Y8-clwA%3D%3D)

## Group Members:
Aaron Joyce
<br/>
Bryan Quirke
<br/>
Erik Eviston
<br/>
Jessa Pajarito
<br/>
Neil Barry-Murphy


<br/><br/><br/>


# Setup Guide

## Using the Flask Application

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
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)


## Logging

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


<br/><br/><br/>


# DDI System Testing Instructions

## In-Depth Testing
(Testing methods for all new required features outlined below)

### Mock DDI Characterisation Data

- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `coke_and_pepsi.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- If successful, click `Select Knowledge Base System`.
- Click `Search DDI Characterization Data`.
- Select `db_1.csv`. Click `View Interactions`.
- When complete, click `Finished - Return to Homepage`.

### Identify drugs in PML

- Integrated with previous step.

### Report un-named PML construct 

- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `unnamed_construct.pml`. Click `Check Validity of Selected File`.
- Error will be explained by system, highlighted in red.
- The line number, and type of construct causing the issue will be highlighted by the system.
- The system will not allow progression beyond this point.

### Report PML construct name-clash 

- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `duplicated_construct.pml`. Click `Check Validity of Selected File`.
- View Results.
- Error will be explained by system, highlighted in red.
- The line number, name and type of construct causing the issue will be highlighted by the system.
- The system will not allow progression beyond this point.

### Identify Parallel DDIs

- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `iden_parallel_ddi_2.pml`. Click `Check Validity of Selected File`.
- Refer to `peos/pml/drugfinder/pml-test-files/iden_parallel_ddi_2.pml` in any editor (such as gedit).
- Two different action constructs refer to two drugs that interact with each other.
- Return to system.
- Click `Analyse File`.
- If successful, click `Select Knowledge Base System`.
- Click `Search DDI Characterization Data`.
- Select `db_1.csv`. Click `View Interactions`.
- When complete, click `Finished - Return to Homepage`.

### PML-TX Save PML to File

- This feature cannot be demonstrated as an isolated article.
- The following transformations highlight the actions of this feature.
- In short, all changes made to files that are transformed are saved by the system, a new file is not created.

### PML-TX Reorder Sequence

- Refer to `peos/pml/drugfinder/pml-test-files/reorder_sequence.pml` in any editor (such as gedit).
- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `reorder_sequence.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- Click `Select Transformation Type`.
- Click `Perform Reorder Sequence`.
- Ensure to select the radio button, and click `Check Validity of Transformation`.
- Again, refer to `peos/pml/drugfinder/pml-test-files/reorder_sequence.pml`.
- Click `Reload` or equivalent. View changes.
- To view side by side changes, find the file of the same name in `peos/pml/drugfinder/duplicate-pml-test-files/`.
- This file is an original copy of the file that was just transformed.
- To redo the test, open a new terminal (in the same directory) and execute:
```bash
cd peos/pml/drugfinder/pml-test-files
```
- From here, revert any changes in git.
```bash
git checkout reorder_sequence.pml
```

### PML-TX Serialise Branch (Naive)

- Refer to `peos/pml/drugfinder/pml-test-files/pml_tx_serialize_branch_naive.pml` in any editor (such as gedit).
- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `pml_tx_serialize_branch_naive.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- Click `Select Transformation Type`.
- Click `Perform Naive Branch Transformation`.
- Ensure to select the radio button, and click `Check Validity of Transformation`.
- Again, refer to `peos/pml/drugfinder/pml-test-files/pml_tx_serialize_branch_naive.pml`.
- Click `Reload` or equivalent. View changes.
- To view side by side changes, find the file of the same name in `peos/pml/drugfinder/duplicate-pml-test-files/`.
- This file is an original copy of the file that was just transformed.
- To redo the test, open a new terminal (in the same directory) and execute:
```bash
cd peos/pml/drugfinder/pml-test-files
```
- From here, revert any changes in git.
```bash
git checkout pml_tx_serialize_branch_naive.pml
```

### PML-TX Serialize Branch (Two-Way)

- Refer to `peos/pml/drugfinder/pml-test-files/pml_tx_serialize_branch_2_way.pml` in any editor (such as gedit).
- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `pml_tx_serialize_branch_2_way.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- Click `Select Transformation Type`.
- Click `Perform Two-Way Branch Transformation`.
- Ensure to select the radio button, and click `Check Validity of Transformation`.
- Again, refer to `peos/pml/drugfinder/pml-test-files/pml_tx_serialize_branch_2_way.pml`.
- Click `Reload` or equivalent. View changes.
- To view side by side changes, find the file of the same name in `peos/pml/drugfinder/duplicate-pml-test-files/`.
- This file is an original copy of the file that was just transformed.
- To redo the test, open a new terminal (in the same directory) and execute:
```bash
cd peos/pml/drugfinder/pml-test-files
```
- From here, revert any changes in git.
```bash
git checkout pml_tx_serialize_branch_2_way.pml
```

### PML-TX Remove Selections (NOT WORKING)

- Refer to `peos/pml/drugfinder/pml-test-files/remove_selection.pml` in any editor (such as gedit).
- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `remove_selection.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- Click `Select Transformation Type`.
- Click `Perform Remove Selections Transformation`.
- Ensure to select the radio button, and click `Check Validity of Transformation`.
- Again, refer to `peos/pml/drugfinder/pml-test-files/remove_selection.pml`.
- Click `Reload` or equivalent. View changes.
- To view side by side changes, find the file of the same name in `peos/pml/drugfinder/duplicate-pml-test-files/`.
- This file is an original copy of the file that was just transformed.
- To redo the test, open a new terminal (in the same directory) and execute:
```bash
cd peos/pml/drugfinder/pml-test-files
```
- From here, revert any changes in git.
```bash
git checkout remove_selection.pml
```

### PML-TX Unroll Iteration

- Refer to `peos/pml/drugfinder/pml-test-files/unroll_iteration.pml` in any editor (such as gedit).
- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `unroll_iteration.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- Click `Select Transformation Type`.
- Click `Perform Unroll Iteration Transformation`.
- Ensure to select the radio button, and click `Check Validity of Transformation`.
- Again, refer to `peos/pml/drugfinder/pml-test-files/unroll_iteration.pml`.
- Click `Reload` or equivalent. View changes.
- To view side by side changes, find the file of the same name in `peos/pml/drugfinder/duplicate-pml-test-files/`.
- This file is an original copy of the file that was just transformed.
- To redo the test, open a new terminal (in the same directory) and execute:
```bash
cd peos/pml/drugfinder/pml-test-files
```
- From here, revert any changes in git.
```bash
git checkout unroll_iteration.pml
```

### PML-TX Parallelise Sequence

- Refer to `peos/pml/drugfinder/pml-test-files/sequence_parallelisation.pml` in any editor (such as gedit).
- Navigate to the homepage.
- Select `Begin Analysis`.
- Select `sequence_parallelisation.pml`. Click `Check Validity of Selected File`.
- Click `Analyse File`.
- Click `Select Transformation Type`.
- Click `Perform Parallelize Sequence Transformation`.
- Ensure to select the radio button, and click `Check Validity of Transformation`.
- Again, refer to `peos/pml/drugfinder/pml-test-files/sequence_parallelisation.pml` in your editor.
- Click `Reload` or equivalent. View changes.
- To view side by side changes, find the file of the same name in `peos/pml/drugfinder/duplicate-pml-test-files/`.
- This file is an original copy of the file that was just transformed.
- To redo the test, open a new terminal (in the same directory) and execute:
```bash
cd peos/pml/drugfinder/pml-test-files
```
- From here, revert any changes in git.
```bash
git checkout sequence_parallelisation.pml
```


<br/><br/><br/>


## Deactivating the Virtual Environment

When finished with analysis of the system, execute:
```bash
deactivate
```
This will disable the virtual environment.


<br/><br/><br/>


# DINTO system (No longer part of the testing branch)

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

## Tests To Handle Incorrect Input

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


<br/><br/><br/>


# Additional System Analysis

## Using the Mongo Database

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
