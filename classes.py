import requests
import pymysql
import DB_info
#import db_informations

class API: 
	def __init__(self): 
		self.url_1 = 'https://world.openfoodfacts.org/cgi/search.pl'
		self.param = {
		'action':'process',
		'tagtype_0':'categories',
		'tag_contains_0':'contains',
		'tag_0':'boisson',
		'page_size':35,
		'json':1
		}

	def request_product(self, tag):
		"""get products from the API"""
		i = 0
		self.param["tag_0"] = tag
		r = requests.get(self.url_1, params=self.param)
		result = r.json()
		data = []
		while i < 20:
			for val in result["products"]:
				try:
					data.append([val["product_name_fr"], \
					val["nutrition_grades"], val["stores_tags"], val["url"]])
				except KeyError:
					pass
				i += 1
		print(data)
		return data

class DB:
	def __init__(self):
		self.host = DB_info.HOST
		self.user = DB_info.USER
		self.password = DB_info.PASSWORD
		self.db = DB_info.DB
		self.connection1 = pymysql.connect(host=self.host, user=self.user, \
		password=self.password)
		self.connection2 = pymysql.connect(host=self.host, user=self.user, \
		password=self.password, db=self.db)

	def createDB(self):
		"""Create database"""
		with self.connection1.cursor() as cursor:
			sql = "CREATE DATABASE IF NOT EXISTS off"
			cursor.execute(sql)
		self.connection.commit()

	def showDB(self):
		"""Show databases"""
		with self.connection1.cursor() as cursor:
			sql = "SHOW DATABASES;"
			cursor.execute(sql)
			result = cursor.fetchall()
			print(result)

	def createTableOpfood(self):
		"""Create opfood's table to store the result of the request to the 
		OpenfoodFact's API"""
		with self.connection2.cursor() as cursor:
			sql = """CREATE TABLE IF NOT EXISTS opfood (
			id int unsigned NOT NULL AUTO_INCREMENT,
			nom varchar(250),
			nutriscore varchar(1),
			store varchar(350),
            url varchar(10000),                         
            PRIMARY KEY (id))
			"""
			cursor.execute(sql)
		self.connection2.commit()

	def describeTable(self, table):
		"""Print the table inserted in parameter"""
		with self.connection2.cursor() as cursor:
			sql = "DESCRIBE {0}".format(table)
			cursor.execute(sql)
			result = cursor.fetchall()
			print(result)

	def dropOpfoodTable(self, table):
		"""Erase the table inserted in parameter"""
		with self.connection2.cursor() as cursor:
			sql = "DROP TABLE IF EXISTS {0}".format(table)
			cursor.execute(sql)
		self.connection2.commit()

	def insert(self, categorie):
		"""Insert products selected by category on parameters into opfood's table"""
		r = API()
		r = r.request_product(categorie)
		with self.connection2.cursor() as cursor:
			for value in r:
				try :
					value_2 = value[2][0]
				except IndexError:
					value_2 = "-"
				sql = "INSERT INTO opfood (nom, nutriscore, store, url) VALUES\
				('%s', '%s', '%s', '%s')" % (value[0], value[1], value_2, \
				value[3])
				cursor.execute(sql)
		self.connection2.commit() 

	def showTable(self, table):
		"""Print the content of the table in parameter by row"""
		with self.connection2.cursor() as cursor:
			sql = "SELECT * FROM {0}".format(table)
			cursor.execute(sql)
			rows = cursor.fetchall()
			for row in rows:
				print("{0} {1} {2} {3} {4}".format(row[0], row[1], row[2],\
				row[3], row[4]))

#class display:
	


r = API()

#r.request_product("farine")
db1 = DB()
#db1.createDB()
#db1.showDB()
db1.dropOpfoodTable("opfood")
db1.createTableOpfood()
db1.describeTable("opfood")
db1.insert("chips")
db1.showTable("opfood")
