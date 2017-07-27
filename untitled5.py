# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 23:53:18 2017

@author: heng
"""

import requests
from bs4 import BeautifulSoup
import lxml.html as lh
import re
 
url = 'https://www.google.com/search'
query = 'Arizona State University'
payload = {'q': query, 'lr': 'lang_en', 'client':'ubntu', 'channel':'fs'}
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"}
r = requests.get(url, params=payload, headers=headers)
soup = BeautifulSoup(r.text)
kno-ecr-pt kno-fb-ctx

name = soup.find('div', class_='kno-ecr-pt kno-fb-ctx _hdf')

if name:
    name.text
    soup.find('span', class_='_Xbe', text=re.compile(".*\d{5}")).text

else:
    soup.find('h3', class_='r').text
    

