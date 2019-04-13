import requests
import pymysql

class API: 
	def __init__(self): 
		self.url_1 = 'https://world.openfoodfacts.org/cgi/search.pl'
		self.param = {
		'action':'process',
		'tagtype_0':'categories',
		'tag_contains_0':'contains',
		'tag_0':'boisson',
		'page_size':20,
		'json':1
		}

	def request(self, tag):
		self.param["tag_0"] = tag
		r = requests.get(self.url_1, params=self.param)
		result = r.json()
		for val in result["products"]:
			print("Nom:", val["product_name_fr"], "note nutritionnelle:", val["nutrition_grades"])
		print(r.url)
		print(result)


#class DataBase(self):
#	def __init__(self):


test = API()

test.request("chips")



