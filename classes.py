import requests
import pymysql
import DB_info
import constantes

class API: 
	"""This class aims to interact with the OpenfoodFact's API. 
	Its parameters aims to prepared the request.
	Its request_product method made the resquest 
	"""
	def __init__(self): 
		"""Parameters for the API request"""
		self.url_1 = 'https://world.openfoodfacts.org/cgi/search.pl'
		self.param = {
		'action':'process',
		'tagtype_0':'categories',
		'tag_contains_0':'contains',
		'tag_0':'',
		'page_size':35,
		'json':1
		}

	def request_product(self, tag):
		"""Get products from the API depending on the tag in parameter. 
		Store the resulte in a list of list named data
		Return data """
		i = 0
		self.param["tag_0"] = tag
		r = requests.get(self.url_1, params=self.param)
		result = r.json()
		data = []
		for val in result["products"]:
			try:
				data.append([val["product_name_fr"], \
				val["nutrition_grades"], val["ingredients_text_fr"], \
				val["stores_tags"], val["url"]])
				i += 1
				if i > 19:
					break
			except KeyError:
				pass
		return data

class DB:
	"""The DB (database) class aims to interact with the database and tables
	using mysql requests.
	It contains the following methods:
	-createCategoriesTable() : create a categories table
	-insertCategoriesTable(): insert categories from a constant file into the 
	categories table and returns a boolean
	-createOpfoodTable(): create opfood's table to store the result of the API's 
	request
	-createSubstituteTable(): create a substitute table to saved the user's 
	substitutes products
	-def deleteTable(table): delete the table passed in parameter
	-def insert(categorie_num): insert products selected by category passed in 
	parameter, in opfood's table
	-def showSmallTable(table): print the content of the rows 0 and 1 of the 
	table passed in parameter
	-def compareNutriscore(nb_product): compares nutriscore's product passed in 
	parameter and proposes a better one, if possible
	-def compareNutriscore(nb_product): compares nutriscore's product
	passed in parameter and proposes a better one (return True), if possible 
	(if not possible (return False)
	-def saveSubstProduct(): insert a substitute product into the 
	susbtitute's table
	-def findSavedProduct(): find saved products in the products's table


	"""
	def __init__(self):
		#information stored in DB_info files with connection informations. 
		self.host = DB_info.HOST
		self.user = DB_info.USER
		self.password = DB_info.PASSWORD
		self.db = DB_info.DB

		#Create the connection parameters
		self.connection = pymysql.connect(host=self.host, user=self.user, \
		password=self.password, db=self.db)

		#Variable used in methods to find a product or a categorie
		self.nb_categorie = 0
		self.product_keys = []

		#Variable to store the categories already search
		self.categorie_searched = []
		

		#Those variables turn into True when so called tables are created, 
		#or when tables informations are stored. To avoid warning messages
		self.create_categories_table_ok = False
		self.insert_categories_table_ok = False
		self.create_opfood_table_ok = False
		self.create_substitute_table_ok = False

	def createCategoriesTable(self):
		"""Create a categories table from a constante file and returns
		a boolean
		"""
		if self.create_categories_table_ok == False: #to avoid warning message
			with self.connection.cursor() as cursor:
				sql = """CREATE TABLE IF NOT EXISTS categories (
				id int unsigned AUTO_INCREMENT,
				categorie varchar(100) NOT NULL,
				PRIMARY KEY (id))"""
				cursor.execute(sql)
			self.connection.commit()
			self.create_categories_table_ok = True
		return self.create_categories_table_ok
	
	def insertCategoriesTable(self):
		"""To insert categories from a constant file into the categories table
		and returns a boolean"""
		if self.insert_categories_table_ok == False: #use the method one time
			with self.connection.cursor() as cursor:
				for categories in constantes.CATEGORIES:
					insert = """INSERT INTO categories (categorie) VALUES 
					("%s")""" % (categories)
					cursor.execute(insert)
			self.connection.commit()
			self.insert_categories_table_ok = True
		return self.insert_categories_table_ok

	def createOpfoodTable(self):
		"""Create opfood's table to store the result of the API's request"""
		if self.create_opfood_table_ok == False: #to avoid warning message
			with self.connection.cursor() as cursor:
				sql = """CREATE TABLE IF NOT EXISTS opfood (
				id int unsigned AUTO_INCREMENT,
				id_categorie int unsigned,
				nom varchar(250),
				nutriscore varchar(1),
				ingredients varchar(50000),
				store varchar(350),
	            url varchar(10000),     
	            PRIMARY KEY (id),                    
	            CONSTRAINT fk_id_categorie #create a foreign key for 
	            	FOREIGN KEY (id_categorie) #categorie row
	            	REFERENCES categories(id))"""
				cursor.execute(sql)
			self.connection.commit()
			self.create_opfood_table_ok = True
		return self.create_opfood_table_ok

	def createSubstituteTable(self):
		"""Create a substitute table to saved the user's substitutes products
		"""
		if self.create_substitute_table_ok == False: #to avoid warning message
			with self.connection.cursor() as cursor:
				sql = """CREATE TABLE IF NOT EXISTS substitute (
				id int unsigned AUTO_INCREMENT,
				id_original int NOT NULL,
				id_substitute int NOT NULL,
				PRIMARY KEY (id))"""
				cursor.execute(sql)
			self.connection.commit()
			self.create_substitute_table_ok = True
		return self.create_substitute_table_ok

	def deleteTable(self, table):
		"""Delete the table passed as parameter"""
		with self.connection.cursor() as cursor:
			sql = "DROP TABLE IF EXISTS {0}".format(table)
			cursor.execute(sql)
		self.connection.commit()

	def insert(self, categorie_num):
		"""Insert products selected by category passed in parameter, 
		into opfood's table
		"""
		#if the categorie is not already in the products table, adds new products
		if categorie_num not in self.categorie_searched: 
			with self.connection.cursor() as cursor:
				#To find the categorie passed as parameter
				sql = ("""SELECT categorie FROM categories WHERE 
				categories.id = {}""").format(categorie_num)
				cursor.execute(sql)
				categorie_name = cursor.fetchall()
				r = API()
				r = r.request_product(categorie_name)
				for value in r:
					try :
						value_3 = value[3][0]
					except IndexError:#to avoid error if the elt doesn't exist
						value_3 = "Pas de lieu connu" 
					sql = """INSERT INTO opfood (id_categorie, nom, nutriscore, ingredients,
					store, url) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")""" % \
					(categorie_num, value[0], value[1], value[2], value_3, value[4])
					cursor.execute(sql)
			self.connection.commit()
		#add in variable the products already searched
		self.categorie_searched.append(categorie_num)
		#add in variable the current categorie 
		self.nb_categorie = categorie_num


	def showSmallTable(self, table):
		"""Print the content of the rows 0 and 1 of the table passed in
		parameter"""
		with self.connection.cursor() as cursor:
			sql = "SELECT * FROM {0}".format(table)
			cursor.execute(sql)
			rows = cursor.fetchall()
			for row in rows:
				print("{0} {1}".format(row[0], row[1]))
			return rows

	def showOpfoodTable(self, num):
		"""Print the content of opfood's table, by categorie passed in parameter"""
		with self.connection.cursor() as cursor:
			sql = "SELECT * FROM opfood WHERE id_categorie = {}".format(num)
			cursor.execute(sql)
			rows = cursor.fetchall()
			for row in rows:
				print("{0} {1} - Nutriscore: {2}".format(row[0], row[2], row[3]))
			return rows

	def compareNutriscore(self, nb_product):
		"""Compares nutriscore's product passed in parameter and proposes a 
		better one (return True), if possible (if not possible (return False)
		"""		
		with self.connection.cursor() as cursor:
			sql = ("SELECT * FROM opfood WHERE id_categorie = {}".format(self.nb_categorie))
			cursor.execute(sql)
			rows = cursor.fetchall()
			origi_prod = 0
			nutri_prod = ""
			final_prod = 0
			#get the id's and original nutriscore's product passed in parameter
			for row in rows: 
				if row[0] == nb_product: 
					orig_prod = row[0]
					nutri_prod = str(row[3])
			#compare nutriscores
			for val in rows: 
				if str(val[3]) < nutri_prod:
					nutri_prod = str(val[3])
					final_prod = val[0]
			#If the original product and the final product are the same, 
			#there is no better product in this selection
			if final_prod == 0:  
				print("Ce produit est déjà au top (toute proportion gardée)")
				return False
			#to print the better product and store a list of ids original 
			#and new products
			else:
				self.product_keys = [nb_product, final_prod]
				for j in rows:
					if j[0] == final_prod:
						print("Voici le produit trouvé : {0} {1} - Nutriscore:\
						{2} ".format(j[0], j[2], j[3])) 
				return True

	def saveSubstProduct(self):
		"""Insert a substitute product into the susbtitute's table"""
		original_key = self.product_keys[0]
		substitute_key = self.product_keys[1]
		with self.connection.cursor() as cursor:
			o_product = ("""INSERT INTO substitute (id_original, id_substitute)\
			VALUES ("%d", "%d")""" % (original_key, substitute_key))
			cursor.execute(o_product)
			print(original_key, substitute_key) #test
			self.connection.commit()


	def findSavedProduct(self):
		"""Find saved products in the products's table"""
		#Join opfood's table and susbtitute's table to find products from ids	
		with self.connection.cursor() as cursor:			
			sql = """SELECT opfood.id, opfood.nom, opfood.nutriscore, 
			opfood.ingredients, opfood.store, opfood.url 
			FROM opfood
			LEFT JOIN substitute
			ON substitute.id_original = opfood.id 
				OR substitute.id_substitute = opfood.id
			WHERE substitute.id_original
				OR substitute.id_substitute
				ORDER BY substitute.id"""
			cursor.execute(sql)
			rows = cursor.fetchall()
			print(rows) #test
			#print the result
			for i, row in enumerate(rows):
				if i % 2 == 0:
					print(i)
					print("\n", i+1, "Produit original: {0}\nNutriscore: {1}\
					\nIngredients: {2}\nTrouver ce produit: {3}\nLien: {4}"\
					.format(row[1], row[2], row[3], row[4], row[5]))
				else:
					print(i)
					print("\n", i+1, "Produit de substitution: {0}\nNutriscore:\
					{1}\nIngredients: {2}\nTrouver ce produit: {3}\nLien: {4}\n\
					".format(row[1], row[2], row[3], row[4], row[5]))

class display:
	"""This class handle the display's methods
		It contains the following methods:
		-def dropIt(): delete every table of the off's database
		-def start(): To start the programme
		-def categorie(self): create and fill the categorie's table using the DB's methods, 
		prints its and store the categorie choose by the user into a variable
		def substitute_search(self):
		-Create and fill the product's table using the DB's methods, 
		prints its and store the product choose by the user into a variable.
		Use the DB's methode to compare nutrigrades to find a better product 
		Return the result of the compareNutriscore's method (Boolean)
		-def save_product(): to store the susbsitituted product or go back to 
		the main menu

		"""
	def __init__(self):
		self.categorie_num = 0
		self.object = DB()
		self.product_num = 0

	def dropIt(self):
		"""Delete every table of the off's database"""
		self.object.deleteTable("opfood")
		self.object.deleteTable("substitute")
		self.object.deleteTable("categories")

	def start(self):
		"""To start the programme"""
		i = 1
		while i == 1:
			try:
				print("1 - Quel aliment souhaitez-vous remplacer?\n2 - \
				Retrouver mes aliments substitués\nVeuillez saisir un numéro:")
				choose_start = input()
				choose_start = int(choose_start)
				if choose_start >0 and choose_start < 3:
					i = 0
					return choose_start
			except ValueError:
				continue

	def categorie(self): 
		"""Create and fill the categorie's table using the DB's methods, 
		prints its and store the categorie choose by the user into a variable"""

		#if the categories's table doesn't exist, creates it
		self.object.createCategoriesTable()
		self.object.insertCategoriesTable()

		i = 1
		while i == 1:
			try:
				(self.object.showSmallTable("categories"))
				print(" Sélectionnez la catégorie en indiquant un chiffre:")
				self.categorie_num = input()
				self.categorie_num = int(self.categorie_num)
				if self.categorie_num in range(1, constantes.NB_CATEGORIES):
					return self.categorie_num
			except ValueError:
				continue

	def substitute_search(self):
		"""Create and fill the product's table using the DB's methods, 
		prints its and store the product choose by the user into a variable.
		Use the DB's methode to compare nutrigrades to find a better product.
		Return the result of the compareNutriscore's method (Boolean) """
		
		#if opfood's table doesn't exist, creates it
		self.object.createOpfoodTable()
		self.object.insert(self.categorie_num)
		i = 1
		while i == 1:
			try:
				range_id = self.object.showOpfoodTable(self.categorie_num)
				#print the products's list and to store ids possible for products's selected
				id_products_selected = [elt[0] for elt in range_id] 
				print("Sélectionnez le produit en indiquant son chiffre pour trouver un produit mieux noté:")
				self.product_num = input()
				self.product_num = int(self.product_num)
				#check if the number wrote by the user is in the range of possible ids
				if self.product_num in id_products_selected: 
					return self.object.compareNutriscore(self.product_num)
			except ValueError:
				continue
		

	def save_product(self):
		"""To store the susbsitituted product or go back to the main menu"""
		i = 1
		while i == 1:
			print("souhaitez-vous sauvegarder le produit proposé (o/n)")
			s_product = input()
			if s_product.lower() == "oui" or s_product.lower() == "o":
				self.object.createSubstituteTable()
				self.object.saveSubstProduct()
				print("Le produit est sauvegardé\n")
				i = 0
			elif s_product.lower() == "non" or s_product.lower() == "n":
				print("Retour au menu")
				i = 0
			else:
				continue 
