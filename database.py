"""This file contains the script to create the database and tables for
the food substitutes program
To create the connection, create a DB_info.py file which contains the following
variables:
HOST = "YourHost"
USER = "YourUserName"
PASSWORD = "YourPassword"
DB = "off"
"""
import pymysql

import DB_info
import constantes


def create_db_and_tables():
    """Function to delete the database if exists, and then creats it.
    It creates categories, prodcuts and substitutes tables, and fills the
    categorie's table"""

    #Create the connection link
    connection1 = pymysql.connect(host=DB_info.HOST, user=DB_info.USER, \
    password=DB_info.PASSWORD)

    #delete the database if exists
    with connection1.cursor() as cursor:
        sql = "DROP DATABASE IF EXISTS off"
        cursor.execute(sql)
    connection1.commit()

    #Create the database
    with connection1.cursor() as cursor:
        sql = "CREATE DATABASE off"
        cursor.execute(sql)
    connection1.commit()

    #Create the connection link
    connection = pymysql.connect(host=DB_info.HOST, user=DB_info.USER, \
    password=DB_info.PASSWORD, db=DB_info.DB)
    #Create a categories table from a constante file
    with connection.cursor() as cursor:
        sql = """CREATE TABLE IF NOT EXISTS categories (
        id int unsigned AUTO_INCREMENT,
        categorie varchar(100) NOT NULL,
        PRIMARY KEY (id))"""
        cursor.execute(sql)
    connection.commit()

    #To insert categories from a constants file into the categories table
    with connection.cursor() as cursor:
        for categories in constantes.CATEGORIES:
            insert = """INSERT INTO categories (categorie) VALUES
            ("%s")""" % (categories)
            cursor.execute(insert)
    connection.commit()

    #Create opfood's table to store the result of the API's request
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
        CONSTRAINT fk_id_categorie #create a foreign key for categorie row
        FOREIGN KEY (id_categorie) 
        REFERENCES categories(id))"""
        cursor.execute(sql)
    connection.commit()

    #Create a substitute table to saved the user's substitutes products
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
