process Pml_Tx_Serialize_Branch{
	branch something{
		action P1{
			requires{patient_records && (intangible)symptoms.status=="increasing"}
			provides{drugList}	
		}
		action Pn{
			script{"Give patient dosage of Fluoxetine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
			provides{"symptoms.status==reduced"}	
		}
	}
}
