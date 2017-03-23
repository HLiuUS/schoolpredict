# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 23:37:39 2017

@author: HengLiu
"""

import urllib2   
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time



#specify the url
url = "http://h1bdata.info/index.php?em=&job=&city=DETROIT&year=All+Years"
header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}  
request = urllib2.Request(url, headers=header)  
response = urllib2.urlopen(request) 
page = response.read() 


#Parse the html in the 'page' variable, and store it in Beautiful Soup format
soup = BeautifulSoup(page)

#print soup.prettify()

all_tables = soup.find_all('table')


right_table=soup.find('table', class_='tablesorter tablesorter-blue hasStickyHeaders')

A=[]
B=[]
C=[]
D=[]
E=[]
F=[]
G=[]

for row in right_table.findAll("tr"):
    cells = row.findAll('td')
    if len(cells)==7: #Only extract table body not heading
        A.append(cells[0].find(text=True))
        B.append(cells[1].find(text=True))
        C.append(cells[2].find(text=True))
        D.append(cells[3].find(text=True))
        E.append(cells[4].find(text=True))
        F.append(cells[5].find(text=True))
        G.append(cells[6].find(text=True))
        
df = pd.DataFrame(A,columns=['EMPLOYER'])
df['JOB TITLE']=B
df['BASE SALARY']=C
df['LOCATION']=D
df['SUBMIT DATE']=E
df['START DATE']=F
df['CASE STATUS']=G
