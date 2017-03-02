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
}
}
