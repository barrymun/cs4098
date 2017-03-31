process Influenza_Treatment{
sequence{
	action assess_patient{
		requires{patient_records && (intangible)symptoms.status=="increasing"}
		provides{drugList}	
	}
	action provide_medication{
		script{"Give patient dosage of lomitapide every 6 hours"}
		agent{Nurse && Carer && Patient}
		provides{"symptoms.status==reduced"}	
	}
	action update_medication{
		script{"Check patient's record and change medication if needed"}
		agent{Doctor&&Nurse && Carer && Patient}
		provides{"symptoms.status==reduced"}	
	}
}
}
