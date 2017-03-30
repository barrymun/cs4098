process Daily_StatinDrink_merge {
  sequence  {
    iteration  {
      action Take_Statin {
        requires { prescription.drug == "statin" }
        provides { therapy.drug == "statin" }
        script{ "Statin to be taken daily, in the evening"}
      }
    }
  }
  sequence  {
    iteration  {
      action Take_Drink {
        requires { shopping.product == "whiskey" } 
        provides { therapy.relax_muscle } 
        script{ "Whiskey (alcohol), to be enjoyed in the evening"} 
      }
    }
  }
}
