# -*- coding: utf-8 -*-
"""
@author: KUjejski for CCAF
"""
import tkinter
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup
import urllib
import html
import csv

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def get_page(url):
    request = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(request)
    soup = BeautifulSoup(page, 'html.parser')
    soup_string = html.unescape(str(soup))
    return soup_string
    

#Reads a list of urls from a CSV and returns the HTMl of the page within a dictionary
def get_html_dicts():
    print("Scraping...")
    tkinter.Tk().withdraw()
    inputfile = askopenfilename()
    with open(inputfile) as inputfile:
        reader = csv.DictReader(inputfile)
        outputDicts = []
        for rowDict in reader:
            try:
                company = rowDict['Organisation']
                htmlString = get_page(rowDict['Website'])
                outputDicts.append({'Company' : company, 'HTML' : htmlString})
            except Exception as e:
                print(str(e))
                print(rowDict)
                continue
    return outputDicts

htmls = get_html_dicts
with open ('output.txt','w',encoding='utf-8') as outputfile:
    for htmlDict in htmls:
        try:
            outputfile.write(htmlDict['Company'] + "\n")
            outputfile.write(htmlDict['Website'] + "\n\n\n")
        except:
            outputfile.write("\nBad URL\n")
            continue