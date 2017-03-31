process IBS_Treatment{
	branch coke_and_pepsi{
		action assess_patient{
			requires{patient_records && (intangible)symptoms.status=="increasing"}
			provides{drugList}	
		}
		action provide_medication{
			script{"Give patient dosage of drugs every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(coke)]"&& patient_records && drug.count=="2" }
			provides{"symptoms.status==reduced"}	
		}
		action provide_more_medication{
			script{"Give patient dosage of drugs every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(pepsi)]"&& patient_records && drug.count=="2" }
			provides{"symptoms.status==reduced"}	
		}
	}
}
