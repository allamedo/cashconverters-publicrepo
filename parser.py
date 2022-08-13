from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config, db, telegram
import os,signal,time,datetime, random
import requests,html5lib

class Product:
  def __init__(self, main_link, category, image, price):
    self.image = image
    self.price = price
    self.id = "CC"+image.split("CC")[1].split("-")[0]+"_0"
    self.main_link = "https://www.cashconverters.es/es/es/comprar/"+category+"/?pid="+self.id
    self.category = category

def parse_products(category="telefonos/moviles/smartphones/apple/iphone-6s-32gb/", index=0, proxy_=None, loop_errors=0):

    products=[]

    if loop_errors > 2: return products

    url="https://www.cashconverters.es/es/es/comprar/"+category+"/?start="+str(index)+"&format=page-element&srule=price-low-to-high"

    if proxy_ is not None: proxy_formated = { "http": "http://"+proxy_, "https": "https://"+proxy_}
    else: proxy_formated= None

    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    try: 
        r  = requests.get(url,proxies=proxy_formated,headers=headers,timeout=9)
        data = r.text

        soup = BeautifulSoup(data, "html5lib")
        
        if soup.find_all('div',class_='col-6 col-sm-6 col-md-4 col-lg-3 col-xl-4') is not None:
            for product in soup.find_all('div',class_='col-6 col-sm-6 col-md-4 col-lg-3 col-xl-4'): #iteramos todos los divs con esa clase
                if product.find('a',class_='product-title') is not None: #si en esta iteracion hay un main link
                    main_link = product.find('a',class_='product-title')['href'] #guardar main link
                if product.find('img') is not None:
                    image = product.find('img')['src'].split("?")[0]
                if product.find('span',class_='price-sales price') is not None:
                    price = product.find('span',class_='price-sales price').text
                    price = price.replace('\n','')
                    price = price.replace('.','')
                    price = price.replace(',','.')
                    price = price.partition(" ")[0]
                    price = float(price)
                products.append(Product(main_link,category,image,price))

        return products

    except:
        print("Error:parse_products Category:"+category+" Index:"+str(index)+" Proxy"+str(proxy_))
        return parse_products(category,index,proxy_,loop_errors+1)

def parse_categories(section="telefonos/moviles/smartphones/apple", loop_errors=0):

    categories =[] 

    if loop_errors >= 2:
        return categories

    url = "https://www.cashconverters.es/es/es/comprar/"+section+"/?start=0&sz=12&format=page-element&catSz=39"

    try: 
        r  = requests.get(url, timeout=3)
        data = r.text

        soup = BeautifulSoup(data, "html5lib")

        if soup.find_all('a',class_='main-link') is not None:
            for categ in soup.find_all('a',class_='main-link') : #iteramos todos los anchor con esa clase
                category = categ['href'] #guardar main link
                if "comprar/" in category:
                    category = category.split("comprar/")[1]
                    category = category[0:-1]
                    categories.append(category)

        return categories
        
    except:
        return parse_categories(section,loop_errors+1)



if __name__ == "__main__":
    
    #categories = [ 
    #    "electrodomesticos/cocina/thermomix/thermomix/vorwerk/tm31/",
    #    "telefonos/moviles/smartphones/apple/iphone-11-64gb/"
    #] 

    while(True):
        print("Parsing started: "+str(datetime.datetime.now()))

        #Listar categorias 	
        categories = db.get_categories()

        #Iterar categorias 
        counter_total = 0
        for category in categories:
            #Calcular low limit price de la categoria
            low_limit_price = db.set_category_price_limit(category) 

            index=0
            num_products = 12
            counter_category=0
            while(num_products>0): #Tomar informacion de productos de la categoria y guardarla en DB - De 12 en 12
                products = parse_products(category,index)
                modified_products = db.insert_replace_products(products) #Actualizar DB
                for product in modified_products:#Comprobar los precios de los productos actualizados 
                    if product.price < low_limit_price:
                        print("Price alert: "+str(product.price)+" ("+str(low_limit_price)+") "+product.main_link)
                        telegram.send_image(product.image)
                        telegram.send_message(product.category+" "+str(product.price)+"€"+" ("+str(low_limit_price)+"€)",product.main_link)
                num_products = len(products)
                index=index+12
                time.sleep(random.randint(1,3))
                counter_category=counter_category+num_products
            counter_total = counter_total + counter_category

            #Buscar precios bajos en los articulos modificados
            low_limit_price = db.set_category_price_limit(category)
                   
            print("Parsed products:"+str(counter_category)+" Low limit price:"+str(low_limit_price)+" Category:"+category)

        print("Parsing finished: "+str(datetime.datetime.now())+" Total parsed products:"+str(counter_total))