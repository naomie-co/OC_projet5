"""This file contains the classes that build the food substitutes program
"""

import warnings
import pymysql
import requests
import DB_info
import database
import constantes


class API:
    """This class aims to interact with the OpenfoodFact's API
    Its parameters aims to prepared the request
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
        Store the result in a list of list named data
        Return data """
        i = 0
        self.param["tag_0"] = tag
        request = requests.get(self.url_1, params=self.param)
        result = request.json()
        data = []
        for val in result["products"]:
            try:
                data.append([val["product_name_fr"],\
                val["nutrition_grades"], val["ingredients_text_fr"],\
                val["stores_tags"], val["url"]])
                i += 1
                if i > 19:
                    break
            except KeyError:
                pass
        return data


class DB:
    """The DB (database) class aims to interact with the database and tables
    using mysql requests
    It contains the following methods:
    -def insert(categorie_num): insert products selected by category passed in
    parameter, in opfood's table
    -def show_small_table(table): print the content of the rows 0 and 1 of the
    table passed in parameter
    -def compare_nutriscore(nb_product): compares nutriscore's product
    passed in parameter and proposes a better one (return True), if possible
    if not possible (return False)
    -def save_substitute(): insert a substitute product in thesusbtitute's
    table
    -def find_saved_product(): find saved products in the products's table
"""
    def __init__(self):
        """information stored in DB_info files with connection informations.
        """
        self.host = DB_info.HOST
        self.user = DB_info.USER
        self.password = DB_info.PASSWORD
        self.database = DB_info.DB

        #Create the connection parameters
        self.connection = pymysql.connect(host=self.host, user=self.user,\
        password=self.password, db=self.database)

        #Variable used in methods to find a product or a categorie
        self.nb_categorie = 0
        self.product_keys = []

        #Variable to store the categories already search
        self.categorie_searched = []

        #object use to send a request to the API
        self.request = API()

    def insert(self, categorie_num):
        """Insert products passed with a number in parameter in opfood's table
        """
        #if the categorie is not already in the products table
        #adds new products
        if categorie_num not in self.categorie_searched:
            with self.connection.cursor() as cursor:
                #To find the categorie passed as parameter
                sql = ("""SELECT categorie FROM categories WHERE
                categories.id = {}""").format(categorie_num)
                cursor.execute(sql)
                categorie_name = cursor.fetchall()
                #send a request to the API from the category passed
                #in parameter
                for value in self.request.request_product(categorie_name):
                    try:
                        value_3 = value[3][0]
                    except IndexError:#to avoid error if the elt doesn't exist
                        value_3 = "Pas de lieu connu"
                    sql = """INSERT INTO opfood (id_categorie, nom, nutriscore, ingredients,
                    store, url) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")""" % \
                    (categorie_num, value[0], value[1], value[2], value_3, value[4])
                    cursor.execute(sql)
            self.connection.commit()
        #add in the variable the products already searched
        self.categorie_searched.append(categorie_num)
        #add in variable the current categorie
        self.nb_categorie = categorie_num

    def show_small_table(self, table):
        """Print the content of rows 0 and 1 of the table passed
        in parameter"""
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {0}".format(table)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                print("{0} {1}".format(row[0], row[1]))
            return rows

    def show_opfood_table(self, num):
        """Print the content of opfood's table, by categorie passed in parameter"""
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM opfood WHERE id_categorie = {}".format(num)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                print("{0} {1} - Nutriscore: {2}".format(row[0], row[2], row[3]))
            return rows

    def compare_nutriscore(self, nb_product):
        """Compares nutriscore's product passed in parameter and proposes a
        better one (return True) if possible (if not possible (return False)
        """
        with self.connection.cursor() as cursor:
            sql = ("SELECT * FROM opfood WHERE id_categorie = {}".format(self.nb_categorie))
            cursor.execute(sql)
            rows = cursor.fetchall()
            nutri_prod = ""
            final_prod = 0
            #get the id's and original nutriscore's product passed in parameter
            for row in rows:
                if row[0] == nb_product:
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
            #Print the better product and store a list of id's original
            #and new products
            else:
                self.product_keys = [nb_product, final_prod]
                for j in rows:
                    if j[0] == final_prod:
                        print("Voici le produit trouvé : {0} {1} - Nutriscore:\
{2} ".format(j[0], j[2], j[3]))
                return True

    def save_substitute(self):
        """Insert a substitute product into the susbtitute's table"""

        original_key = self.product_keys[0]
        substitute_key = self.product_keys[1]
        with self.connection.cursor() as cursor:
            o_product = ("""INSERT INTO substitute (id_original, id_substitute)\
            VALUES ("%d", "%d")""" % (original_key, substitute_key))
            try:
                cursor.execute(o_product)
                self.connection.commit()
                print("Le produit est sauvegardé\n")
            #if the original product is already in the table
            except pymysql.err.IntegrityError:
                print("Ce produit orignial est déjà sauvegardé, vous pouvez le \
retrouver dans vos produits sauvegardés\n")
                self.connection.commit()


    def find_saved_product(self):
        """Find saved products in the products's table"""

        #Count used to print the number of the product which is printed
        product_count = 1
        #Request to find product in opfood's table form the original id stored
        #in the substitute table
        with self.connection.cursor() as cursor:
            original_sql = """SELECT * FROM opfood where id IN\
            (SELECT id_original FROM substitute)"""
            cursor.execute(original_sql)
            original_product = cursor.fetchall()

            #if there are no produits saved, print a message
            if original_product == ():
                print("Aucun produit sauvegardé\n")

            #print the orginial product
            for index, row in enumerate(original_product):
                print("\n", product_count, "Produit original: {0}\nNutriscore: {1}\
\nIngredients: {2}\nTrouver ce produit: {3}\nLien: {4}".format(row[2], row[3],\
row[4], row[5], row[6]))
                product_count += 1

                #Search and print the substitute product from the original_id
                substitute_sql = ("SELECT * FROM opfood WHERE id IN \
                (SELECT id_substitute FROM substitute \
                WHERE id_original={})".format(row[0]))
                cursor.execute(substitute_sql)
                substit = cursor.fetchall()
                for ind, elt in enumerate(substit):
                    print("\n", product_count, "Produit de substitution: {0}\nNutriscore: \
{1}\nIngredients: {2}\nTrouver ce produit: {3}\nLien: {4}\n".format(elt[2], \
elt[3], elt[4], elt[5], elt[6]))
                    product_count += 1


class Display:
    """This class handle the Display's methods
        It contains the following methods:
        -def start(): questions asked in the menu
        -def categorie(self): prints and store the categorie choose
        by the user into a variable
        -def substitute_search(self): create and fill the product's 
        table using the DB's methods, prints its and store the product 
        choose by the user into a variable. Use the DB's methode to compare
        nutrigrades to find a better product. Return the result of the 
        compare_nutriscore's method (Boolean)
        -def save_product(): to store the susbsitituted product or go back to
        the main menu
        -def application(self): method to interact with the user. Called by 
        the main.py file
        """

    def __init__(self):
        self.categorie_num = 0
        self.object = DB()
        self.product_num = 0
        self.choose_start = 0

    def start(self):
        """To start the program, question's asked in the menu"""

        i = True
        while i:
            try:
                print("1 - Quel aliment souhaitez-vous remplacer?\n2 - \
Retrouver mes aliments substitués\n3 - Quitter\n Veuillez saisir un chiffre:")
                self.choose_start = input()
                self.choose_start = int(self.choose_start)
                if self.choose_start > 0 and self.choose_start < 4:
                    i = False
            except ValueError:
                continue

    def categorie(self):
        """Prints and store the categorie choose by the user into a variable"""

        i = True
        while i:
            try:
                (self.object.show_small_table("categories"))
                print(" Sélectionnez la catégorie en indiquant un chiffre:")
                self.categorie_num = input()
                self.categorie_num = int(self.categorie_num)
                if self.categorie_num in range(1, constantes.NB_CATEGORIES):
                    i = False
            except ValueError:
                continue
        return self.categorie_num

    def substitute_search(self):
        """Create and fill the product's table using the DB's methods,
        prints its and store the product choose by the user into a variable.
        Use the DB's methode to compare nutrigrades to find a better product.
        Return the result of the compare_nutriscore's method (Boolean) """

        #insert product in product table only if the categorie is not already in the table
        self.object.insert(self.categorie_num)
        i = True
        while i:
            try:
                range_id = self.object.show_opfood_table(self.categorie_num)
                #print the products's list and to store ids possible for
                #products's selected
                id_products_selected = [elt[0] for elt in range_id]
                print("Sélectionnez le produit en indiquant son chiffre pour \
trouver un produit mieux noté:")
                self.product_num = input()
                self.product_num = int(self.product_num)
                #check if the number wrote by the user is in the range of possible ids
                if self.product_num in id_products_selected:
                    i = False
                    return self.object.compare_nutriscore(self.product_num)
            except ValueError:
                continue


    def save_product(self):
        """To store the susbsitituted product or go back to the main menu"""
        i = True
        while i:
            print("souhaitez-vous sauvegarder le produit proposé (o/n)")
            s_product = input()
            if s_product.lower() == "oui" or s_product.lower() == "o":
                self.object.save_substitute()
                i = False
            elif s_product.lower() == "non" or s_product.lower() == "n":
                print("Retour au menu")
                i = False
            else:
                continue

    def application(self):
        """Method to interact with the user. Called by the main.py file"""

        #to avoid warning message
        warnings.filterwarnings("ignore")

        #Creates the database, tables and insert categories in categories table
        database.create_db_and_tables()


        application_loop = True

        while application_loop:
            #main menu
            self.start()

            #choose a product in categories and find a better product
            if self.choose_start == 1:
                self.categorie()
                if self.substitute_search():
                    self.save_product()
                else:
                    continue

            #to end the program
            elif self.choose_start == 3:
                application_loop = False
            #to find products saved

            else:
                self.object.find_saved_product()
        print("\nA bientôt")
