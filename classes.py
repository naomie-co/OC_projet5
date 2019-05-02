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
					data.append([val["product_name_fr"], val["nutrition_grades"], val["stores_tags"], val["url"]])
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
		self.connection1 = pymysql.connect(host=self.host, user=self.user, password=self.password)
		self.connection2 = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db)

	def createDB(self):
		with self.connection1.cursor() as cursor:
			sql = "CREATE DATABASE IF NOT EXISTS off"
			cursor.execute(sql)
		self.connection.commit()

	def showDB(self):
		with self.connection1.cursor() as cursor:
			sql = "SHOW DATABASES;"
			cursor.execute(sql)
			result = cursor.fetchall()
			print(result)

	def createTableOpfood(self):
		with self.connection2.cursor() as cursor:
			sql = """CREATE TABLE IF NOT EXISTS opfood (
			id int unsigned NOT NULL AUTO_INCREMENT,
			nom varchar(200),
			nutriscore varchar(1),
			store varchar(10000),
            url varchar(10000),                         
            PRIMARY KEY (id))
			"""
			cursor.execute(sql)
		self.connection2.commit()

	def describeTable(self):
		with self.connection2.cursor() as cursor:
			sql = "DESCRIBE opfood;"
			cursor.execute(sql)
			result = cursor.fetchall()
			print(result)

	def dropOpfoodTable(self):
		with self.connection2.cursor() as cursor:
			sql = "DROP TABLE IF EXISTS opfood"
			cursor.execute(sql)
		self.connection2.commit()

	def insert(self):
		r = API()
		r = r.request_product("boisson")
		with self.connection2.cursor() as cursor:
			for value in r:
				sql = "INSERT INTO opfood (nom, nutriscore, store, url) VALUES ('%s', '%s', '%s', '%s')" % (value[0], value[1], value[2], value[3])
				cursor.execute(sql)
		self.connection2.commit()

	def showTable(self):
		with self.connection2.cursor() as cursor:
			sql = "SELECT * FROM opfood"
			cursor.execute(sql)
			rows = cursor.fetchall()
			for row in rows:
				print("{0} {1} {2} {3}".format(row[0], row[1], row[2], row[3]))

#class display:
	


r = API()

#r.request_product("farine")
db1 = DB()
#db1.createDB()
#db1.showDB()
db1.dropOpfoodTable()
db1.createTableOpfood()
db1.describeTable()
db1.insert()
db1.showTable()
