process identify_parallel{
	branch something{
		action P1{
			script{"Give patient dosage of Dicyclomine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(dicyclomine,(9:00),drugid),(donepezil,(8:30,20:30),drugid)]"&& patient_records && drug.count=="2" }
			provides{"symptoms.status==reduced"}	
		}
		action Pn{
			script{"Give patient dosage of Fluoxetine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
			provides{"symptoms.status==reduced"}	
		}
	}
}
