import classes


go = 1

db1 = classes.DB()
disp = classes.display()

disp.dropIt()

while go == 1:
	if disp.start() == 1:
		disp.categorie()
		if disp.substitute_search() == True:
			disp.save_product()
		else:
			continue
	else: 
		db1.createSubstituteTable()
		db1.findSavedProduct()