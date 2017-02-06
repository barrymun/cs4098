# Overwatch

### Group Members:
Aaron Joyce, Bryan Quirke, Erik Eviston, Jessa Pajarito, Neil Barry-Murphy

### Activate the virtual environment:

```bash
source env/bin/activate
```

### Using the PEOS system to analyse a PML file:

The PML file used here is: peos/compiler/models/lib_checkout.pml
Execute the following:

```bash
bash setup.sh
```

### Parse some OWL from the DINTO ontology and report some statistic about the file contents:

Information is printed alongside the results.
Execute the following:

```python
python readowl.py
```

Execute:
```bash
deactivate
```
when finished.