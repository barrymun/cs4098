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


Note: Please ignore the instructables.txt file. This is a reference for the group only.

# File Selection and Analysis as a Flask Application

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
Install necessary requirements, with root permissions (if above command fails):
```bash
sudo pip install -r requirements.txt
```
Navigate to the homepage:
```bash
http://127.0.0.1:5000/
```
If you cannot access the webpage at this point, restart mongo again:
```bash
sudo service mongod restart
```
And restart the application:
```python
python app.py
```

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

## Please Ignore All Below This Section (See Above)

### Using the PEOS system to analyse a PML file:
The PML file used here is: peos/compiler/models/lib_checkout.pml. Execute the following:

```bash
bash setup.sh
```

### Parse some OWL from the DINTO ontology and report some statistic about the file contents:
Information is printed alongside the results.
Execute the following:
```python
python readowl.py
```

NOTE: If the above command fails, it means the permissions are not correctly set for the 
root user on your virtual machine or device.
<br/>
Execute:
```bash
sudo pip install ontospy
```
to fix.

Execute:
```bash
deactivate
```
when finished.
