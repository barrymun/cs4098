# Overwatch

### Group Members:
Aaron Joyce, Bryan Quirke, Erik Eviston, Jessa Pajarito, Neil Barry-Murphy

Note: Please ignore the instructables.txt file. This is a reference for the group only.

### Activate the virtual environment:

```bash
source env/bin/activate
```

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
root user on your virtual machine or device. Execute:
```bash
sudo pip install ontospy
```
as a quick fix.

Execute:
```bash
deactivate
```
when finished.
