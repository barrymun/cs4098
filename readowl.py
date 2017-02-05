import ontospy

model = ontospy.Ontospy("DINTO_inf_mech.owl")
model.classes
#print(model.classes)
model.properties
#print(model.properties)
model.printClassTree()
model.toplayer
print "Here is the directory structure of the file"
print(model.toplayer)
a_class = model.getClass("DINTO_000001")
a_class = a_class[0]
print "Here is the first class"
print(a_class)

#a_class.serialize()
print "Here are the parent(s) of the first class"
print(a_class.parents())
print "Here are the children of the first class"
print(a_class.children())
print "Here is the actual data contained in the first class"
print(a_class.serialize())