process IBS_Treatment{
    sequence flatten{
        action something{
        }
        action assess_patient{
            requires{patient_records && (intangible)symptoms.status=="increasing"}
            provides{drugList}  
        }
        action provide_medication{
            script{"Give patient dosage of Dicyclomine every day"}
            agent{Nurse && Carer && Patient}
            requires{drug.list=="[(coke),(pepsi)]"&& patient_records && drug.count=="2" }
            provides{"symptoms.status==reduced"}  
        }
    }
}
