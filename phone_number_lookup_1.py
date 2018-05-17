import requests
from lxml import html
import sys
import pymysql
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import time
import random
import string
import pandas as pd

headers={'User-Agent': 'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", 
       "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
       "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
       )
ua = UAS[random.randrange(len(UAS))]
headers = {'user-agent':ua}
translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))


def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

# signal TOR for a new connection 
def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="1234")
        controller.signal(Signal.NEWNYM)


def db_connection():
	conn= pymysql.connect("localhost","root","root","lookup")
	cur=conn.cursor()
	return conn,cur


def search_phone(number):
	number=number.translate(translator)
	number="".join(number.split())
	print(number)
	final_result=[]
	streetaddress,locality,region,pcode=("" for i in range(4))
	url="https://www.yellowpages.com/search?search_terms="+number+"&geo_location_terms=global"
	try:
		r=requests.get(url,verify=False,timeout=30,headers=headers)
		print(r.status_code)
		soup=BeautifulSoup(r.content,"html.parser")
		addresses=soup.findAll(class_='street-address')

		if addresses:
			with open('output/'+number+'.txt','w',encoding='utf-8') as f:
			
				for address in addresses:
					streetaddress=address.text
					for i in soup.findAll(class_='locality'):
						locality=i.text.replace('\xa0', '')
					for x in soup.findAll("span",itemprop="addressRegion"):
						region=x.text
					for y in soup.findAll("span",itemprop="postalCode"):
						pcode=y.text
					result={'number':number,'streetaddress':streetaddress,'locality':locality,'region':region,'pcode':pcode}
					final_result.append(result)
				print(final_result)
				f.write(str(final_result))
				f.close()
		return 1,final_result
	except:
		print('>>>>>>>>>>error')
			

if __name__ == '__main__':

	# number='518-234-2000'
	# number=sys.argv[1]
	indputdata=pd.read_csv('contacts_1.csv').head(100)
	indputdata=indputdata.Domain
	# print(session.get("http://httpbin.org/ip").text)
	for i in indputdata:
		time.sleep(2)
		search_phone(i)
