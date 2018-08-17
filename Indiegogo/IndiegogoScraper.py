# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 16:03:53 2018

@author: ujejskik
"""

from selenium import webdriver
import time 
from datetime import datetime
import re
import random
from progress.counter import Counter
from progress.bar import IncrementalBar
import urllib 
from bs4 import BeautifulSoup
import html
import csv
import tkinter
from tkinter.filedialog import askopenfilename



#Request header text for user-agent spoofing - some hosts will refuse headerless requests to prevent blatant scraping
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def getProjectData(link):
    request = urllib.request.Request(link, headers=hdr)
    page = urllib.request.urlopen(request)
    soup = BeautifulSoup(page, 'html.parser')
    soupString = html.unescape(str(soup))
    try:
        
        title = re.findall('<meta content="(.*?)" name="sailthru.title"/>', soupString)[0]
        amountPledged = re.findall(',"forever_funding_combined_balance":(.*?),"is_external_campaign"', soupString)[0]
        country = [re.findall('<meta content="(.*?)" name="keywords"/>',soupString)[0].split(',')[-1]][0]
        currency = re.findall(',"currency":{"iso_code":"(.*?)","symbol"',soupString)[0]
        deadline = re.findall('<meta content="(.*?)" name="sailthru.expire_date">',soupString)[0]
        numBackers = re.findall('<meta content="(.*?)" name="sailthru.displayed_contributions"/>',soupString)[0]
        goalPercentage = re.findall('<meta content="(.*?)%" name="sailthru.displayed_pct_funded"/>',soupString)[0]
        category = re.findall('<meta content="(.*?)" name="sailthru.displayed_category"/>',soupString)[0]
    except Exception as e:
        print(link)
        print(str(e))
        return []
    projectDict = {"Title": title, "Amount_Pledged": amountPledged, "Country": country, "Currency": currency, "Deadline": deadline, "Backers": numBackers, "Percentage_Funded": goalPercentage, "Category": category}
    return projectDict

    
def getProjectLinks(url):
    print("Gathering links...")
    projectLinks = set()
    browser = webdriver.Firefox("C:\Program Files\gecko")
    browser.get(url)
    #Wait for website to load
    time.sleep(5)
    #Closes cookie-acceptance pop-up
    try:
        browser.find_element_by_css_selector('#CybotCookiebotDialogBodyLevelButtonAccept').click()
    except:
        pass
    counter = Counter("Propagating webpages")
    #Simulates click on 'view more' button until exhausted
    while(True):
        try:
            #waits random time to prevent DDOS ban
            time.sleep(random.uniform(0.2, 1.3))
            browser.find_element_by_css_selector('a.ng-isolate-scope').click()
        except:
            break
        counter.next()
    counter.finish()
    links = browser.find_elements_by_xpath("//a[@href]")
    for bigl in links:
        #Ensures that the link is a valid project
        if "/projects/" in bigl.get_attribute("href") and "/coming_soon/" not in bigl.get_attribute("href"):
            projectLinks.add(bigl.get_attribute("href"))
    browser.quit()
    return projectLinks

def getProjects(url):
    projectLinks = getProjectLinks(url)
    bar = IncrementalBar("Scraping projects...", max=len(projectLinks))
    dictList = []
    try:
        for p in projectLinks:
            try:
                projectDict = getProjectData(p)
            except urllib.HTTPError as e:
            #If a URLError is raised, this is likely due to the frequency of requests to the webpage
            #To overcome this, a pause is added before reattempting to scrape the project
                print("%s/n%s" % (str(url), str(e)))
                time.sleep(30)
                projectDict = getProjectData(p)
            #Empty projectDict indicates error/invalid link
            if projectDict:
                dictList.append(projectDict)
            else:
                print 
            bar.next()
            time.sleep(random.uniform(0.2, 2.1))
        bar.finish()
    #If an exception is raised, dictList is returned to prevent loss of progress
    except Exception as e:
        print(str(e))
        pass   
    return dictList

#Calculates ETA of completion by taking average completion time per category link
def getETA(timeTotal, currentStep, totalSteps):
        return ((timeTotal/currentStep)*(totalSteps-currentStep))/60



tkinter.Tk().withdraw()
inputfile = askopenfilename()
with open(inputfile, 'r',encoding='utf-8') as infile:
    categoryList = infile.readlines()
    infile.close()

timeTotal = 0
#categoryList = ["https://www.indiegogo.com/explore/audio?project_type=campaign&project_timing=all&sort=most_funded"]
fieldnames = ["Title","Amount_Pledged","Country","Currency","Deadline","Backers","Percentage_Funded", "Category"]
with open("IndiegogoOutput1.csv",'a',encoding = 'utf-8') as outputFile:
    writer = csv.DictWriter(outputFile, fieldnames, extrasaction='ignore',lineterminator='\n')
    #writer.writeheader()
    c=1
    print("Scraping sites...")
    for categoryLink in categoryList:
        sTime = time.time()
        print("%s/%s : %s" % (c, len(categoryList), categoryLink))
        results = getProjects(categoryLink)
        writer.writerows(results)
        timeTaken = time.time() - sTime
        timeTotal += timeTaken
        print("Completed in %s seconds. ETA: %s minutes" % (str(timeTaken), str(getETA(timeTotal,c,len(categoryList)))) )
        c = c+1
    
input("Press any key to continue...")
