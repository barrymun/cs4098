process Influenza_Treatment{
sequence{
	action assess_patient{
		requires{patient_records && (intangible)symptoms.status=="increasing"}
		provides{drug}	
	}
	action provide_medication{
		script{"Give patient dosage of lomitapide every 6 hours"}
		agent{Nurse && Carer && Patient}
		requires{drug.id == "CHEBI_72297" || drug.name=="lomitapide"}
		provides{"symptoms.status==reduced"}	
	}
}
}
