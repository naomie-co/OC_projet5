import warnings
import pymysql

import DB_info
import constantes

#to avoid warning messages
warnings.filterwarnings("ignore")
		
def create_db_and_tables():


	connection1 = pymysql.connect(host=DB_info.HOST, user=DB_info.USER, \
	password=DB_info.PASSWORD)

	with connection1.cursor() as cursor:
		sql = "DROP DATABASE IF EXISTS off"
		cursor.execute(sql)
	connection1.commit()


	with connection1.cursor() as cursor:
		sql = "CREATE DATABASE off"
		cursor.execute(sql)
	connection1.commit()

#Create the connection parameters
	connection = pymysql.connect(host=DB_info.HOST, user=DB_info.USER, \
	password=DB_info.PASSWORD, db=DB_info.DB)
	"""Create a categories table from a constante file and returns
	a boolean
	"""
	with connection.cursor() as cursor:
		sql = """CREATE TABLE IF NOT EXISTS categories (
		id int unsigned AUTO_INCREMENT,
		categorie varchar(100) NOT NULL,
		PRIMARY KEY (id))"""
		cursor.execute(sql)
	connection.commit()


	"""To insert categories from a constant file into the categories table
	and returns a boolean"""
	with connection.cursor() as cursor:
		for categories in constantes.CATEGORIES:
			insert = """INSERT INTO categories (categorie) VALUES 
			("%s")""" % (categories)
			cursor.execute(insert)
	connection.commit()


	"""Create opfood's table to store the result of the API's request"""
	with connection.cursor() as cursor:
		sql = """CREATE TABLE IF NOT EXISTS opfood (
		id int unsigned AUTO_INCREMENT,
		id_categorie int unsigned,
		nom varchar(255),
		nutriscore varchar(1),
		ingredients text,
		store varchar(255),
		url text, 
		PRIMARY KEY (id),
		CONSTRAINT fk_id_categorie #create a foreign key for 
		FOREIGN KEY (id_categorie) #categorie row
		REFERENCES categories(id))"""
		cursor.execute(sql)
	connection.commit()
	
	"""Create a substitute table to saved the user's substitutes products
	"""
	with connection.cursor() as cursor:
		sql = """CREATE TABLE IF NOT EXISTS substitute (
		id int unsigned AUTO_INCREMENT,
		id_original int NOT NULL UNIQUE,
		id_substitute int NOT NULL,
		PRIMARY KEY (id))"""
		cursor.execute(sql)
	connection.commit()


if __name__ == '__main__':
	create_db_and_tables()