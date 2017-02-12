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
![alt tag](https://github.com/barrymun/cs4098/tree/master/static/missing-team-member.png)


Note: Please ignore the instructables.txt file. This is a reference for the group only.

### Activate the virtual environment:
```bash
source venv/bin/activate
```

# PML/OWL-DINTO File selection and Loading as a Flask Application

Activate the virtual environment (Python 2.7 required):
```bash
source venv/bin/activate
```
Install necessary requirements:
```bash
pip install -r requirements.txt
```
If above command fails for permissions reasons, execute the following:
```bash
sudo pip install -r requirements.txt
```
Run the flask application:
```python
python app.py
```
If the above command fails, restart mongo:
```bash
sudo service mongod restart
```
Navigate to the homepage:
```bash
http://127.0.0.1:5000/
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
```bash
use app
```
List all currently available collections:
<br/>
(Should be empty prior to launching the flask app)
```bash
db.getCollectionNames()
```
List all pml files in the project:
```bash
db.dist.files.find()
```
List all pml files that you have selected as a user:
```bash
db.dist.selected.find()
```
List all pml files that have been analysed:
```bash
db.dist.analysis.find()
```