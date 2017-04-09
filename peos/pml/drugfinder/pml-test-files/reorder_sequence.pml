process test_reorder_it{
	sequence seq0 {
		action ab3bd89764b3211720664b070265c11d8 {
			requires{patient_records && (intangible)symptoms.status=="increasing"}
			provides{drugList}
		}
		action ae65247e8fb23fdc8c7779d9b2f56db47 {
			script{"Give patient dosage of Fluoxetine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
			provides{"symptoms.status==reduced"}
		}
		action a3ba2473cb4b5859d05028740a793dc02 {
			script{"Give patient dosage of Fluoxetine every day"}
			agent{Nurse && Carer && Patient}
			requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
			provides{"symptoms.status==reduced"}
		}
	}
} /*reorder [0,2,1]
