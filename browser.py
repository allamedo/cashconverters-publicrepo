from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from requests.exceptions import ConnectionError, Timeout
import config, globals, db, parser
import os,signal,time,datetime,random

def open_browser(proxy_=None, loop_errors=0):
	
	if loop_errors == 0: print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": Opening broswer with proxy: " + str(proxy_))

	if loop_errors >= 2:
		print("Loop errors. Closing")
		globals.driver.quit()
		exit()

	options = webdriver.ChromeOptions()
	if proxy_ is not None:
		options.add_argument('--proxy-server=http://' + proxy_)

	#Abrir navegador cuando este disponible
	while True:
		try:
			globals.driver = webdriver.Remote("http://browser:4444/wd/hub", DesiredCapabilities.CHROME, options=options)
			break
		except:    
			print("Waiting for browser...")
			time.sleep(5)

	url = 'https://www.cashconverters.es/es/es/comprar/telefonos/moviles/smartphones/apple'
	globals.driver.get(url)
	time.sleep(2)

	#Aceptar cookies	
	try:
		globals.driver.find_element("class name",("ui-dialog-buttonset").find_elements("tag name","*")[1].click()
	except:
		None
	#Cerrar promocion emergente
	try:
		globals.driver.find_element("class name",("ui-dialog-titlebar-close").click()
	except:
		None

def parse_categories(section="telefonos/moviles/smartphones/apple", loop_errors=0):

	categories =[] 

	if loop_errors >= 2:
		return categories

	url = "https://www.cashconverters.es/es/es/comprar/"+section

	globals.driver.get(url)
	time.sleep(1)
	globals.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(5)

	#Expandir categorias
	try:
		globals.driver.execute_script("arguments[0].click();",globals.driver.find_element("class name",("view-more-button"))
		time.sleep(5)
	except:
		None

	try:
		for category in globals.driver.find_elements("class name","product-title"):
			if url in category.get_attribute('href'):
				category = category.get_attribute('href').split("comprar/")[1]
				category = category[0:-1]
				categories.append(category)

	except:
		return parse_categories(section, loop_errors+1)

	return categories

def stop_process(signalNumber, frame):
	if globals.driver:
		print("Stopping process. Closing browser...")
		globals.driver.close()
		quit()
	return

if __name__ == "__main__":

	#Que hacer si se solicita parar el proceso
	signal.signal(signal.SIGTERM, stop_process) #desde el sistema 
	signal.signal(signal.SIGINT, stop_process)#desde el telcado 


#	proxies = ["88.198.50.201:6500", "199.187.125.84:12300","167.114.8.255:3130","51.83.217.212:3130","51.38.84.226:3130","51.255.103.2:3130"]

	if "PROXY" in os.environ:
		proxy = os.environ['PROXY']
	else:
		proxy = None

	open_browser(proxy)

	sections = [
		"https://www.cashconverters.es/es/es/comprar/telefonos/moviles/smartphones/apple",
		"https://www.cashconverters.es/es/es/comprar/telefonos/moviles/smartphones/samsung/",
		"https://www.cashconverters.es/es/es/comprar/electrodomesticos/cocina/thermomix/thermomix/vorwerk/",
		"https://www.cashconverters.es/es/es/comprar/electrodomesticos/limpieza/aspiradoras/aspirador-robot/irobot/",
		"https://www.cashconverters.es/es/es/comprar/videojuegos-y-consolas/consolas/",
		"https://www.cashconverters.es/es/es/comprar/informatica/ordenador-portatil/portatil-apple/apple/",
		"https://www.cashconverters.es/es/es/comprar/informatica/ordenador-sobremesa/apple/apple/",
		"https://www.cashconverters.es/es/es/comprar/relojes/smartwatch/apple/"
	] 

	for section in sections:
		section = section.split("https://www.cashconverters.es/es/es/comprar/")[1]
		categories = parse_categories(section)
		db.insert_replace_categories(categories)

	globals.driver.close()




