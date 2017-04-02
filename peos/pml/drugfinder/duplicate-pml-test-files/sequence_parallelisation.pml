process test_seq_par{
    sequence seq0 {
        action a9ca1108c15842b931461a6da19a053e4 {
            requires{patient_records && (intangible)symptoms.status=="increasing"}
            provides{drugList}
        }
        action a8c069b23952a922ae3495e9ec5491825 {
            script{"Give patient dosage of Fluoxetine every day"}
            agent{Nurse && Carer && Patient}
            requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
            provides{"symptoms.status==reduced"}
        }
        action a1524a39c86c81b47d2191cdf11a5b2af {
            script{"Give patient dosage of Fluoxetine every day"}
            agent{Nurse && Carer && Patient}
            requires{drug.list=="[(fluoxetine,(9:00),drugid)]"&& patient_records && drug.count=="1" }
            provides{"symptoms.status==reduced"}
        }
    }
}
