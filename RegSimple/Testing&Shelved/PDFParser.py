# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 14:44:30 2018

@author: ujejskik
"""
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen
import urllib.request as ul
from urllib.parse import urlparse, urljoin
import time
from random import randint
import multiprocessing as mp

from Blacklists import BLACKLIST, INVALID_TYPES 

class PDFParser:
    rDepth = int()
    visited = set() 
    pdfLinks = set()
    country = str()
    inputURL=str()
    currentURL= str()
    
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    
    #Constructor
    #def __init__(self, _regURL, _country):
       # self.inputURL = _regURL
       # self.country = _country
        
    def getPDFs(self, _url):
        self.pdfLinks.clear()
        self.visited.clear()
        self.inputURL = _url
        # self.rDepth = _rDepth
        self.rDepth = 3
        self.recPDFCrawl(self.inputURL, 0)
        return self.pdfLinks
        
    # Parses all internal domain links into a list
    def recPDFCrawl(self, url, r_level):
        #print(str(url) + ": " + str(r_level))
        global currentURL 
        currentURL = url
        self.visited.add(url)
        parsed_uri = urlparse(url)
        # Parses domain substring
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        # Generates list of all links
        try:
            urls = self.getlinks(url)
            unvisited_domains = []
            for link in urls:
                if(link.endswith('.pdf') or link.endswith('.PDF')):
                    self.pdfLinks.add(link)
                elif ((domain in link) and self.linkValid(link) and not(link in self.visited)):
                    unvisited_domains.append(link)
            #print(unvisited_domains)
            if (not unvisited_domains or (r_level == self.rDepth)):
                return
            else:
                for link in unvisited_domains:
                    if not(link in self.visited):
                        time.sleep(randint(99,501)/float(100))
                        self.recPDFCrawl(link, r_level+1)
        except Exception as e:
            print(str(url) + ": " + str(e) + str(time.strftime(" %I:%M:%S")))
            pass
        return            
        #return internal_domains
    
    # Generates list of all links on a webpage
    def getlinks(self,url):
        # Stores page's html as object
        request = ul.Request(url, headers=self.hdr)
        page = urlopen(request) 
        a_tag = SoupStrainer('a')
        soup = BeautifulSoup(page, 'lxml', parse_only = a_tag)
        urls = []
        # Parses all urls into list
        for anchor in soup.findAll('a', href=True):
            link = anchor.get('href')
            if not(link.startswith('http')):
                link = urljoin(url, link)
            link.replace(" ", "")
            urls.append(link)
        return urls
    
    def linkValid(self,link):
        if ((not self.blacklisted(link,BLACKLIST)) and self.validType(link)):
            return True
        else:
            return False
    
    def blacklisted(self, link, blacklist):
        for banned_domain in blacklist:
            if banned_domain in link:
                return True
        return False
    
    def validType(self, link):
        urlTokens = link.split('.')
        if(('.' + urlTokens[-1]) in INVALID_TYPES):
            return False
        else:
            return True

queue = ["http://www.bcv.cv/vEN/Pages/Homepage.aspx","http://www.banguat.gob.gt/default.asp?lang=2","http://www.sib.gob.gt/web/sib/inicio"]
if __name__ == '__main__':
    p = mp.Pool(4)
    print(p.map(PDFParser.getPDFs(),queue))
    k=input("press close to exit")