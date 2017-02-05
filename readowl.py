import ontospy

model = ontospy.Ontospy("DINTO_inf_mech.owl")
model.classes
#print(model.classes)
model.properties
#print(model.properties)
model.printClassTree()
model.toplayer
print(model.toplayer)
a_class = model.getClass("DINTO_000001")
a_class = a_class[0]
print(a_class)
#print(a_class.serialize())
#a_class.serialize()
print(a_class.parents())
print(a_class.children())