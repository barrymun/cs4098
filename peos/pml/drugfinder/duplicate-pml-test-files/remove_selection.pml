process test_removal {
	selection sample_selection {
		action a1 {
			requires{patient_records && (intangible)symptoms.status=="increasing"}
			provides{drugList}
		}
		action a2{
			script{"Give patient dosage of Fluoxetine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
			provides{"symptoms.status==reduced"}
		}
		action a3{
			script{"Give patient dosage of Fluoxetine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
			provides{"symptoms.status==reduced"}
		}
	}
} less [a2,a3]
