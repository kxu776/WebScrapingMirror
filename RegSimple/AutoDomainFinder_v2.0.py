# -*- coding: utf-8 -*-
"""
@author: ujejskik
"""
'''
---------- NOTES ----------
REGSIMPLE Scraper v2.0 - This script intends to scrape websites for PDFs, which are subsequently filtered for specific terms.
SEE: CSVreader.py for excel filtering example.

It accepts a CSV input containing a list of countries and their corresponding financial regulator/central bank.
SEE: FinReg.csv

It then iterates through every link in the input CSV, recursively scraping every site and returning a list of every PDF link found on the site (In dictionary form).
This data is written to a CSV file, containing the PDFs URL, Country and Title. (And potentially Year of publication in the future).
----------------------------
'''

from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen
import urllib.request as ul
from urllib.parse import urlparse, urljoin
import time
import tkinter
from tkinter.filedialog import askopenfilename
from random import randint
from Blacklists import BLACKLIST, INVALID_TYPES 
import csv

#Constant defining maximum recursion depth
R_DEPTH = 3

###Defined as sets due to O(1) access performance as compared with O(n) of lists
#List of visited webpages
visited = set()

#DictList of all PDF links found
pdfLinks = []

#URL of webpage currently being scraped
currentURL= str()

#Header for user-agent spoofing 
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


# Recursively crawls entire website for all PDF links
def recPDFCrawl(url, r_level):
    #print(str(url) + ": " + str(r_level))
    global currentURL 
    currentURL = url
    #Marks current URL as visited
    visited.add(url)
    parsed_uri = urlparse(url)
    # Parses domain substring
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    # Generates list of all links
    try:
        urls = getlinks(url)
        unvisited_domains = []
        #Stores all .PDF links found
        for linkDict in urls:
            if(('.pdf' in str(linkDict["URL"]) or '.PDF' in str(linkDict["URL"]))):
                pdfLinks.append(linkDict)
            #Adds all unvisted internal domains to list for expansion
            elif ((domain in linkDict["URL"]) and linkValid(linkDict["URL"]) and not(linkDict["URL"] in visited)):
                unvisited_domains.append(linkDict["URL"])
        #Ends recursive expansion if Maximum expansion depth is reached, or if no more unvisted pages are found
        if (not unvisited_domains or (r_level == R_DEPTH)):
            return
        else:
            #Visits all unvisted urls designated for expansion
            for link in unvisited_domains:
                if not(link in visited):
                    #Random wait to prevent spamming requests
                    time.sleep(randint(99,501)/float(100))
                    #Recursive call 
                    recPDFCrawl(link, r_level+1)
    except Exception as e:
        print(str(url) + ": " + str(e) + str(time.strftime(" %I:%M:%S")))
        pass
    return            

# Generates list of all links on a webpage - Returns linkDict
def getlinks(url):
    request = ul.Request(url, headers=hdr)
    page = urlopen(request) 
    #Creates soup of all anchor tags (i.e. links) on webpage
    soup = BeautifulSoup(page, 'lxml', parse_only = SoupStrainer('a'))
    urls = []
    # Parses all urls into list
    for anchor in soup.findAll('a', href=True):
        linkDict = {'Country': "", 'URL': "", 'Title': "", 'Year' : "", 'Document Type' : "" }
        #Assumes text in anchor tag as title
        linkDict['Title'] = anchor.string
        link = anchor.get('href')
        #If link uses content disposition (ie incomplete url), prefixes domain to form complete URL.
        if not(link.startswith('http')):
            link = urljoin(url, link)
        linkDict['URL'] = link
        urls.append(linkDict)
    return urls

#Return boolean result of link validity check
def linkValid(link):
    if ((not blacklisted(link,BLACKLIST)) and validType(link)):
        return True
    else:
        return False

#Checks if link belongs to manually blacklisted domains.
#Takes as params: the link to be checked, and a manually constructed blacklist(List of banned domains as strings)
def blacklisted(link, blacklist):
    for banned_domain in blacklist:
        if banned_domain in link:
            return True
    return False

#Filters out non-html urls to prevent recursive scraping dead-end
#Takes as param: link to be checked
def validType(link):
    urlTokens = link.split('.')
    if(('.' + urlTokens[-1]) in INVALID_TYPES):
        return False
    else:
        return True
  
#File chooser for inputFile    
tkinter.Tk().withdraw()
inputfile = askopenfilename()

#Column names for output CSV file
fieldnames = ['Country','URL','Title','Year','Document Type']
#Opens input CSV, containing list of Countries and URLS of their central bank/regulator
with open(inputfile) as inputfile:
    reader = csv.DictReader(inputfile)
    with open('FocusedResults7.csv', 'w', encoding ='utf-8') as outputfile:
        writer = csv.DictWriter(outputfile, fieldnames, extrasaction='ignore',lineterminator='\n')
        #Writes column names to output file
        writer.writeheader()
        print("Initialising scraping...")
        try:
            #For every row of input CSV
            for inputDict in reader:
                print(inputDict['URL'])
                print(str(time.strftime(" %I:%M:%S")))
                #Clears URL collection variables between scraping each site
                visited.clear()
                pdfLinks.clear()
                #Reads country corresponding to link from csv
                inputCountry = inputDict['Country']
                #Gathers all PDF links on site, beggining with URL read from CSV
                recPDFCrawl(inputDict['URL'],0)
                #Writes every PDF found to seperate row in outputfile, along with its corresponding country
                for pdfDict in pdfLinks:
                    pdfDict['Country'] = inputCountry
                    writer.writerow(pdfDict)
        except (KeyboardInterrupt, SystemExit):
            outputfile.close()
            print(currentURL)
            raise
        except Exception as e:
            print(str(e) + str(time.strftime(" %I:%M:%S")))
            pass
    print("Done.")
    outputfile.close()
    input("Press Enter to continue...")