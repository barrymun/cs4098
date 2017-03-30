process IBS_Treatment{
sequence seq_name{
	action assess_patient{
		requires{patient_records && (intangible)symptoms.status=="increasing"}
		provides{drugList}	
	}
	action provide_medication{
		script{"Give patient dosage of Dicyclomine every day"}
		agent{Nurse && Carer && Patient}
		requires{drug.list=="[(dicyclomine,(9:00),drugid),(donepezil,(8:30,20:30),drugid)]"&& patient_records && drug.count=="2" }
		provides{"symptoms.status==reduced"}	
	}
}
}
