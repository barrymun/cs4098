#!/usr/bin/env bash
echo "Testing drugfinder..."
echo "Drug list format := [(drug_name,drug_timings,drug_id),(drug2_name,drug2_timings,drug2_id) ..]"
echo
cd peos/pml/drugfinder
echo "Finding drugs in flu.pml"
echo
./drugFind flu.pml
cat drug_list.txt

echo
echo "Finding drugs in allergy.pml"
echo
./drugFind allergy.pml
cat drug_list.txt
echo

echo "Finding drugs in depression.pml"
echo
./drugFind depression.pml
cat drug_list.txt
echo
