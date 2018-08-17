# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 12:57:25 2018

@author: ujejskik
"""
import csv 
import tkinter
from tkinter.filedialog import askopenfilename

#### IF TITLE = EMPTY THEN ADD


def getTitle(url):
    urltokens = url.split("/")
    title = urltokens[-1]
    if(title.endswith('.pdf') or title.endswith('.PDF')):
        title = title[:-4]
    title = title.replace("%20"," ")
    return title

tkinter.Tk().withdraw()
inputfile = askopenfilename()
titles = []
with open(inputfile) as inputfile:
    reader = csv.DictReader(inputfile)
    with open('FocusedResults.csv','w') as outputfile:
        fieldnames = ['Country','URL','Title','Year','Document Type']
        writer = csv.DictWriter(outputfile, fieldnames, extrasaction='ignore',lineterminator='\n')
        writer.writeheader()
        print("Generating titles...")
        for row in reader:
            title = getTitle(row['URL'])
            row['Title'] = title
            writer.writerow(row)
        print("Done.")
        inputfile.close()
        outputfile.close()    