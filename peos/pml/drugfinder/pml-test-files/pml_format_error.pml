process Influenza_Treatment{
sequence{
	action assess_patient{
		requires{patient_records && (intangible)symptoms.status=="increasing"}
		provides{drugList}	
	}
	action provide_medication{
		script{"Give patient dosage of lomitapide every 6 hours"}
		agent{Nurse && Carer && Patient}
		requires{drug.count=="2" && patient_records && drug.list=="[(lomitapide,(12:30,6:30),drugid),(paracetamol,(4:30,7:30),drugid)]"}
		provides{"symptoms.status==reduced"}	
	}
	action update_medication{
		script{"Check patient's record and change medication if needed"}
		agent{Doctor&&Nurse && Carer && Patient}
		requires{drug.count=="2" && patient_records && drug.list=="[(amlodipine,(8:00),drugid),(amoxicillin,(8:00),drugid)]"}
		provides{"symptoms.status==reduced"}	
	}
}

