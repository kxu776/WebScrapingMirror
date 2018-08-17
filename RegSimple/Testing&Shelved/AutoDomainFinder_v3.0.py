# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 17:54:29 2018

@author: ujejskik
"""

from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen
import urllib.request as ul
from urllib.parse import urlparse, urljoin
import time
import tkinter
from tkinter.filedialog import askopenfilename
import pandas as pd
from random import randint
from Blacklists import BLACKLIST, INVALID_TYPES 
import multiprocessing as mp

R_DEPTH = 3

#defined as sets due to O(1) access performance as compared with O(n)
visited = set()
pdfLinks = set()
currentURL= str()

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


# Parses all internal domain links into a list
def recPDFCrawl(url, r_level):
    #print(str(url) + ": " + str(r_level))
    global currentURL 
    currentURL = url
    visited.add(url)
    parsed_uri = urlparse(url)
    # Parses domain substring
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    # Generates list of all links
    try:
        urls = getlinks(url)
        unvisited_domains = []
        for link in urls:
            if(link.endswith('.pdf') or link.endswith('.PDF')):
                pdfLinks.add(link)
            elif ((domain in link) and linkValid(link) and not(link in visited)):
                unvisited_domains.append(link)
        #print(unvisited_domains)
        if (not unvisited_domains or (r_level == R_DEPTH)):
            return
        else:
            for link in unvisited_domains:
                if not(link in visited):
                    time.sleep(randint(99,501)/float(100))
                    recPDFCrawl(link, r_level+1)
    except Exception as e:
        print(str(url) + ": " + str(e) + str(time.strftime(" %I:%M:%S")))
        pass
    return            
    #return internal_domains

# Generates list of all links on a webpage
def getlinks(url):
    # Stores page's html as object
    request = ul.Request(url, headers=hdr)
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

def linkValid(link):
    if ((not blacklisted(link,BLACKLIST)) and validType(link)):
        return True
    else:
        return False

def blacklisted(link, blacklist):
    for banned_domain in blacklist:
        if banned_domain in link:
            return True
    return False

def validType(link):
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


'''
tkinter.Tk().withdraw()
inputfile = askopenfilename()
with open(inputfile) as inputfile:
    regURLs = inputfile.readlines()
    regURLs = [x.strip() for x in regURLs]
inputfile.close()
with open('Batch1Output4.txt', 'w', encoding="utf-8") as file:
    print("Initialising scraping...")
    try:
        for startDomain in regURLs:
            print(str(startDomain) + str(time.strftime(" %I:%M:%S")))
            visited.clear()
            pdfLinks.clear()
            recPDFCrawl(startDomain,0)
            file.write((startDomain)+"\n\n")
            for pdf in pdfLinks:
                file.write(str(pdf) + "\n")
            file.write("\n\n\n")
    except (KeyboardInterrupt, SystemExit):
        file.close()
        print(currentURL)
        raise
    except Exception as e:
        print(e + str(time.strftime(" %I:%M:%S")))
        pass
print("Done.")
file.close()
'''


'''
def worker(working_queue, output_queue):
    while True:
        if working_queue.empty() == True:
            break #this is the so-called 'poison pill'    
        else:
            url = working_queue.get()
            print(multiprocessing.current_process())
            p = PDFParser(url,"Test")
            output_queue.put(p.getPDFs(3))
    return

if __name__ == '__main__':
    print("Something")
    static_input = ["http://www.bcv.cv/vEN/Pages/Homepage.aspx","http://www.banguat.gob.gt/default.asp?lang=2","http://www.sib.gob.gt/web/sib/inicio"]
    working_q = multiprocessing.Queue()
    output_q = multiprocessing.Queue()
    results_bank = []
    p = multiprocessing.Pool()
    p.map(worker, static_input)
'''