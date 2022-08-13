import MySQLdb, numpy, warnings, time, datetime
import config

host = config.db['host']
user = config.db['user']
passw = config.db['passw']
db_ = config.db['db_']
port = config.db['port']

class Product:
  def __init__(self, main_link, category, image, price):
    self.image = image
    self.price = price
    self.id = "CC"+image.split("CC")[1].split("-")[0]+"_0"
    self.main_link = "https://www.cashconverters.es/es/es/comprar/"+category+"/?pid="+self.id
    self.category = category

def insert_replace_products(products):
	db = MySQLdb.connect(host, user, passw, db_, port, charset='utf8', connect_timeout=0)
	cursor = db.cursor()

	modified_products = []  

	for product in products:

		cursor.execute("SELECT * FROM `cashconverters` WHERE `id` = '" + product.id + "'")
		if cursor.rowcount > 0 and product.price < float(cursor._rows[0][3]):#Si el producto ya existia pero su precio ha bajado, actualizar price_updated 
			warnings.filterwarnings('ignore', category=MySQLdb.Warning)
			cursor.execute("UPDATE `cashconverters` SET `price` = %s,"
						   "`thumb_url` = %s, `category` = %s, `price_updated` = now(), `last_seen` = now()"
						   " WHERE `id` = %s",
						   (product.price, product.image, product.category, product.id))
			modified_products.append(product)
			print("Replaced: "+product.id+" Price: "+str(product.price))

		elif cursor.rowcount > 0 and product.price >= float(cursor._rows[0][3]):#Si el producto ya existia pero su precio no ha bajado, actualizar last_seen 
			warnings.filterwarnings('ignore', category=MySQLdb.Warning)
			cursor.execute("UPDATE `cashconverters` SET `last_seen` = now()"
						   " WHERE `id` = '" + product.id + "'")

		elif cursor.rowcount == 0:#Si el producto no existia, añadirlo
			warnings.filterwarnings('ignore', category=MySQLdb.Warning)
			cursor.execute(
				"REPLACE INTO `cashconverters` (`id`, `price`,`thumb_url`,`price_updated`,`last_seen`,`category`) "
				"VALUES (%s,%s,%s,now(),now(),%s)",
				(product.id, product.price, product.image, product.category.encode("utf-8", "ignore"),))
			modified_products.append(product)
			print("Added: "+product.id+" Price: "+str(product.price))

	db.commit()

	return modified_products

def insert_replace_categories(categories):
	db = MySQLdb.connect(host, user, passw, db_, port, charset='utf8', connect_timeout=0)
	cursor = db.cursor()

	for category in categories:

		cursor.execute("SELECT * FROM `cashconverters_categ` WHERE `category` = '" + category + "'")
		if cursor.rowcount == 0:
			warnings.filterwarnings('ignore', category=MySQLdb.Warning)
			cursor.execute(
				"REPLACE INTO `cashconverters_categ` (`category`) "
				"VALUES (%s)",
				(category.encode("utf-8", "ignore"),))

			print("Added: "+category)

	db.commit()

def set_category_price_limit(category):
	db = MySQLdb.connect(host, user, passw, db_, port, charset='utf8', connect_timeout=0)
	cursor = db.cursor()

	price_low_limit = 0
	prices = []
	
	#Listar precios 	
	cursor.execute("SELECT * FROM `cashconverters` WHERE `category` = '" + category + "'  ORDER BY `price` ASC")
	for price in cursor._rows:
		prices.append(float(price[3]))

	if len(prices) > 0:
		prices_std = numpy.std(prices)
		prices_mean = numpy.mean(prices)
		anomaly_cut_off = prices_std * 3

		price_low_limit  = prices_mean - anomaly_cut_off
		price_low_limit = round(price_low_limit,2)

		#Insertar precio medio si el anterior era 0 o era mayor que el nuevo	
		cursor.execute("SELECT * FROM `cashconverters_categ` WHERE `category` = '" + category + "'")
		old_price_low_limit = cursor._rows[0][2]
		if old_price_low_limit == 0 or price_low_limit < old_price_low_limit:
			warnings.filterwarnings('ignore', category=MySQLdb.Warning)
			cursor.execute("UPDATE `cashconverters_categ` SET `price_low_limit` = %s, `date` = now()"
							" WHERE `category` = %s",
							(price_low_limit, category))
			db.commit()
			return price_low_limit
		else: return old_price_low_limit

	return price_low_limit


def get_categories():
	db = MySQLdb.connect(host, user, passw, db_, port, charset='utf8', connect_timeout=0)
	cursor = db.cursor()

	categories = [] 

	cursor.execute("SELECT * FROM `cashconverters_categ`")
	for category in cursor._rows:
		categories.append(category[0])

	return categories

def get_products(category):
	db = MySQLdb.connect(host, user, passw, db_, port, charset='utf8', connect_timeout=0)
	cursor = db.cursor()

	products = [] 

	cursor.execute("SELECT * FROM `cashconverters` WHERE `category` = '" + category + "'")
	for product in cursor._rows:
		products.append(Product("/"+product[0]+".html", product[4],product[5],product[3]))

	return products

if __name__ == "__main__":


	#print(set_category_price_limit("electrodomesticos/cocina/thermomix/thermomix/vorwerk/tm31"))

	
	#Insertar productos  
	products=[]
	products.append(Product("es/es/segunda-mano/thermomix-vorwerk-tm31/CC088_E247404_0.html?cgid=686-cod_c-8-vorwerk-catalogado-531579",
	"electrodomesticos/cocina/thermomix/thermomix/vorwerk/tm31",
	"https://images.cashconverters.es/productslive/smartphone/apple-iphone-6s-32gb_CC049_E587168-0_0.jpg?d=medium",
	430.93))

	for product in insert_replace_products(products):
		print(product.id)
	
	"""
	#Imprimir productos bajos de precio
	for category in get_categories():
		low_limit_price = set_category_price_limit(category)
		for product in get_products(category):
			if product.price < low_limit_price:
				print("https://www.cashconverters.es/es/es/"+product.category+"/"+product.id+".html")
	"""