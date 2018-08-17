# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 14:22:11 2018

@author: ujejskik
"""
'''
----------------------------
A collection of CSV filtering methods - For use with the REGSIMPLE scraping database.
----------------------------
'''

import csv 
import tkinter
from tkinter.filedialog import askopenfilename

#Returns all rows containing the terms specified in filter [], in either the title or url string.
def getFocusedResults():
    filter = ['AML', 'A M L', 'A_M_L', 'Anti', 'Laundering', 'Counter', 'CFT', 'Proceeds', 'Prevention', 'Deterring', 'Detecting', 'Beneficial', 'Owners', 'Intelligence', 'Organized' 'crime', 'Casinos', 'Suspicious', 'transactions', 'FATF', 'F A F T', 'F_A_F_T']
    links = []
    
    tkinter.Tk().withdraw()
    inputfile = askopenfilename()
    with open(inputfile, encoding='utf-8') as inputfile:
        reader = csv.DictReader(inputfile)
        print("Filtering...")
        for row in reader:
            for f in filter:
                if f.upper() in row['URL'].upper() or f.upper() in row['Title']:
                   links.append(row)
                
    with open('AMLResults2.csv','w', encoding='utf-8') as csvfile:
        fieldnames = ['Country','URL','Title','Year','Document Type']
        writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore',lineterminator='\n')
        print("Printing rows ...")
        writer.writeheader()
        writer.writerows(links)
        print("Done.")
        csvfile.close()
        
#Returns all rows containing explicitly English docs (unfortunately not a common convention to specify language in url).
def getEnglishResults():        
    filter = ['/english/','/English/','/en/','/EN/','/ENG/','/en-US/','/eng-docs/','_ingles', 'www.ecb.europa.eu/ecb/legal','www.ecb.europa.eu/internal_market']
    links = []
    
    tkinter.Tk().withdraw()
    inputfile = askopenfilename()
    with open(inputfile) as inputfile:
        reader = csv.DictReader(inputfile)
        print("Filtering...")
        for row in reader:
            for f in filter:
                if f in row['URL']:
                   links.append(row)
                
    with open('FilteredNonEnglishURLs.csv','w') as csvfile:
        fieldnames = ['Country','URL','Title','Year','Document Type']
        writer = csv.DictWriter(csvfile, fieldnames, extrasaction='ignore',lineterminator='\n')
        print("Printing rows ...")
        writer.writeheader()
        writer.writerows(links)
        print("Done.")
        csvfile.close()
        
#getEnglishResults()
getFocusedResults()