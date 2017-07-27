# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 10:49:50 2017

@author: heng
"""

import urllib2
from bs4 import BeautifulSoup

User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
header = {}
header['User-Agent'] = User_Agent

url = 'https://www.us-proxy.org/'
req = urllib2.Request(url,headers=header)
res = urllib2.urlopen(req).read()

soup = BeautifulSoup(res)
ips = soup.findAll('tr')
f = open("proxy","w")

for x in range(1,len(ips)-1):
    ip = ips[x]
    tds = ip.findAll("td")
    porttype = 'http'
    if tds[6].contents[0] == 'yes':
        porttype = 'https'
    ip_temp = porttype + '\t' + tds[0].contents[0]+ "\t" + tds[1].contents[0]+'\n'
    # print tds[2].contents[0]+"\t"+tds[3].contents[0]
    f.write(ip_temp)
    

import urllib
import socket

socket.setdefaulttimeout(3)
f = open("proxy")
lines = f.readlines()

url = "https://www.google.com"
proxys = []

for line in lines:
    ip = line.strip("\n").split("\t")
    proxy_host = ip[0] + '://' + ip[1] + ":" + ip[2]    
    proxy_temp = {ip[0]:proxy_host}
    proxys.append(proxy_temp)
    
url = "https://www.google.com"

for proxy in proxys:
    try:
        res = urllib.urlopen(url,proxies=proxy).read()
        print proxy, 'is working'
    except Exception,e:
        print "Bad Proxy", proxy
        continue    
    