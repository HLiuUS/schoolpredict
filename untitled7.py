# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 22:30:49 2017

@author: heng
"""
import requests
from bs4 import BeautifulSoup

url = "http://www.priceline.com/l/hotels/express-deals.htm"
headers = {"User-Agent": "Priceline 12.1 rv:121000051 (iPhone; iPhone OS 8.1.2; en_US)",
           "Accept-Encoding": "gzip",
           "Content-Type": "application/json",
           }
payload = {'cityName': 'Dearborn, MI', 
           'checkInDate': '04/20/2017', 
           'checkOutDate': '04/22/2017', 
           'numberOfRooms': '1'
           }
r = requests.post(url, headers=headers, params=payload)
soup = BeautifulSoup(r.text)

https://www.priceline.com/stay/search/hotels/Washington,+DC/20170414/20170417/1/?searchType=CITY&page=1&dealType=EXPRESS_DEAL

city = 'washington'
state = 'DC'
address = city + ',+' + state

checkInDate = '20170414'
checkOUtDate = '20170417'
numberOfRooms = '1'


baseurl = 'https://www.priceline.com/stay/search/hotels'
url = '/'.join([baseurl, address, checkInDate, checkOUtDate, numberOfRooms])
payload = {'searchType': 'CITY', 'dealType': 'EXPRESS_DEAL', 'starRatings':'4'}
r = requests.get(url, params=payload, headers=headers)


ng-binding: 4.5 star...
areaname-line ng-binding :downtown

class="ng-binding ng-scope" : We choose the hotel, you save 32%