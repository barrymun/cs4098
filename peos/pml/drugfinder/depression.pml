process Depression_Treatment{
sequence{
	action assess_patient{
		requires{patient_records && (intangible)symptoms.status=="increasing"}
		provides{drugList}	
	}
	action provide_medication{
		script{"Give patient dosage of Fluoxitine every day"}
		agent{Nurse && Carer && Patient}
		requires{drug.list=="[(fluoxitine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
		provides{"symptoms.status==reduced"}	
	}
}
}