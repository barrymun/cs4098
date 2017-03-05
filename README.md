# Overwatch

# Zero Velocity Release Guide

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
<br/>
![Left Game](https://raw.githubusercontent.com/barrymun/cs4098/master/static/missing-team-member.png?token=AO6TcC4OfL6ceSkoyhC508no4nOT6hycks5YqZLDwA%3D%3D)

# Using the Flask Application

Activate the virtual environment (Python 2.7 required):
```bash
source venv/bin/activate
```
Run the setup script:
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

Once the app has been started, open another terminal in the same directory and execute:
```bash
tail -f info.log
```
Ensure to activate the virtual environment (venv).

# In-Depth Testing
Please note that all explanations are accompanied by images.
<br/>
See the `documentation/testing/testing-process` section of this repo for more information.

- Navigate to the homepage (process described above).
- Select "Begin Analysis".
- Select a pml file of your choice.
- "depression.pml" describes only one drug, and will list all interactions of that drug.
- "irritable_bowel_syndrome.pml" describes multiple (2) drugs, and will list the interactions between these 2 drugs.
- When a file has been selected, click "Check Validity of Selected File" to continue.
- The next page displayed is the results of a pml file check.
- The result will be either valid or invalid. An invalid result will not allow for progression.
- If result is valid, click "Analyse File" to extract the drug information.
- You will now be presented with a list containing drug information realting to the title of the pml. (ie - depression will yield a prescription of fluoxetine)
- Click "Search DINTO for Interactions" to continue.
- Next, select the DINTO knowledge base. For the purposes of this test, the only KB is "test_selection.owl".
- Select the file, and click "Load Knowledge Base" to continue.
- A list of drug-drug interactions will now be displayed on screen.
- See the "Info" header for more information on how to test single-instance drug interactions.
- Select "Finished" when analysis is complete. You will be redirected to the homepage.

# Feature List, and Quick Testing

## (1) PML File Selection

Navigate to the home page. Click on the "PML Analysis" button.
<br/>
Select any number of files from the presented menu, and click "Load Selected Files" when ready.
<br/><br/>
To quickly try an example with two successful tests and one unsuccessful test, select the following files:

## (2) PML File Loading

Ensure that your selected files from the previous section are correct.
<br/>
Navigate to the previous page if necessary.
<br/>
Note that if navigating backwards, all files from a previous selection will not be persisted.
<br/>
(You will have to reselect all files).
<br/>
When ready, select the "Analyse PML Files" button.

## (3) Running PML analysis

From the previous section, select the "Analyse PML Files" button.
<br/>
This will use the PEOS system to analyse any and all specified files.
<br/>
The results will be displayed on screen.

## (4) On-Screen PML reporting

The results of any successfully analysed tests will be displayed. Any errors will also be presented.

## (5) PML Error and Warning Highlights

Errors, from the previous section, will be highlighted by the system.
<br/>
These may include errors within the actual files themselves.

## (6) PML Log File Generation

A logfile with all information regarding the analysis of the files will be created.
<br/>
This is named "info.log", and is generated in the root directory.
<br/>
A second log file, "info.log.1" is also created to handle information that would otherwise be displayed in the terminal.

## (7) Select Specific OWL Ontology

Navigate to the home page. Click on the "DINTO Reporting" button.
<br/>
Select any number of files from the presented menu, and click "Load Selected Files" when ready.

## (8) Load Selected Ontology

Ensure that your selected files from the previous section are correct.
<br/>
Navigate to the previous page if necessary.
<br/>
Note that if navigating backwards, all files from a previous selection will not be persisted.
<br/>
(You will have to reselect all files).
<br/>
When ready, select the "Analyse OWL Files" button.

## (9) On-Screen DINTO Reporting

The results of any successfully analysed tests will be displayed. Any errors will also be presented.

## (10) DINTO Logfile Generation

Uses the same Logfile as the PML reporting feature. The two systems, however, are clearly differentiated.

## (11) DINTO Error and Warning Highlights

Errors, from section 9, will be highlighted by the system.
<br/>
These may include errors within the actual files themselves.

# Using the Mongo Database
Installation for Ubuntu 16.04 will be handled by the setup script.
<br/>
Open a terminal and execute the following:
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
List all pml files in the project:
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

When finished with your analysis if the system, execute:
```bash
deactivate
```
This will disable the virtual environment.
