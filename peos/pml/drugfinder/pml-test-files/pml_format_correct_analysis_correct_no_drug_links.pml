process Allergy_Treatment{
sequence{
	action assess_patient{
		requires{patient_records && (intangible)symptoms.status=="increasing"}
		provides{drugList}	
	}
	action provide_medication{
		script{"Give patient 1 table of Loratadine each day until Rashes clear up,Hydrocortone in the morning and in the evening and Paracetamol every 6 hours"}
		agent{Nurse && Carer && Patient}
		requires{drug.count=="2" && drug.list=="[(loratadine,(8:00),drugid),(hydrocortone,(8:30,20:30),drugid),(paracetamol,(9:00,15:00),drugid)]" &&patient_records}
		provides{"symptoms.status==reduced"}	
	}
}
}
