# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 10:05:02 2018

@author: ujejskik
"""
'''
---------- NOTES -----------
This script intends to scrape project information from Kickstarter for the purpose of non-commercial research data collection.

It will take a .txt file input of line-seperated links to kickstarter pages, fileterd by: country, category and success-state(assumes all displayed projects are successful).
Link eg: https://www.kickstarter.com/discover/advanced?state=successful&category_id=17&woe_id=23424975&sort=end_date&seed=2554907&page=

CAVEAT: At the time of writing (08/18),  Kickstarter has implemented a hard limit on iteration of 200 pages, beyond which iteration is impossible.
        THIS SCRAPER WILL NOT WORK if more than 2400 (12projects*200pages) projects exist after applying the filters (Country/Category/SuccessState) - any projects beyond #2400 WILL NOT BE SCRAPED
----------------------------
'''
from bs4 import BeautifulSoup
import urllib
import re
import html
from progress.spinner import Spinner
import csv
import datetime


projects = set()


print("Initialising scraping...")
spinner = Spinner('Scraping')
#Iterates through 200 pages (This is a limit imposed by kickstarter)
for num in range (1,201):
    #Currently link input is manual, but batch link input from txt file will be addad.
    #increments page number each iteration
    link = urllib.request.urlopen('https://www.kickstarter.com/discover/advanced?state=successful&category_id=33&woe_id=23424975&sort=end_date&seed=2555224&page='+str(num)).read()
    #using BS to parse
    soup = BeautifulSoup(link, 'html.parser')
    #gets project 'card' elements
    projectDivs = soup.find_all("div", class_="js-react-proj-card col-full col-sm-12-24 col-lg-8-24")
    if projectDivs:
        for div in projectDivs:
            #Converts project htmls to plaintext so that regex can be used for parsing
            projects.add(html.unescape(str(div)))
    else:
    #If no projects are found on a page, it assumes that all projects have been found so iteration ends.
        print("\n" + str(num) + " pages scraped")
        break
    spinner.next()
spinner.finish()


projectDicts = []
#Column names for output CSV file
fieldnames = ["Title","Amount_Pledged","Country","Currency","Deadline","Backers","Static_USD_Rate","USD_Pledged","Category"]   
with open('KickstarterScraperOutput.csv', 'a', encoding ='utf-8') as outputfile:
        writer = csv.DictWriter(outputfile, fieldnames, extrasaction='ignore',lineterminator='\n')
        writer.writeheader()
        for div in projects:
        #Parses each project into a dict which is written to output CSV file, utilising regex. 
            title = re.findall('},"name":(.*?),"blurb":',div)
            amountPledged = re.findall(',"pledged":(.*?),"state"', div)
            country = re.findall(',"country":(.*?),"currency"', div)
            currency = re.findall(',"currency":(.*?),"currency_symbol"', div)
            unixDeadlineDate = re.findall(',"deadline":(.*?),"state_changed_at"', div)
            #deadlineDate = [datetime.datetime.fromtimestamp(int(unixDeadlineDate[0])).strftime('%Y-%m-%d')]
                #Converts date from Unix time to datetime if required.
            numBackers = re.findall(',"backers_count":(.*?),"static_usd_rate"',div)
            staticUSDRate = re.findall(',"static_usd_rate":(.*?),"usd_pledged"', div)
            USDPledged = re.findall(',"usd_pledged":(.*?),"converted_pledged_amount"', div)
            category = re.findall('}}},"category":{"id":\d*?,"name":(.*?),"slug":', div)
            projectDict = {"Title" : title[0], "Amount_Pledged" : amountPledged[0], "Country" : country[0], "Currency" : currency[0], "Deadline" : unixDeadlineDate[0], "Backers" : numBackers[0], "Static_USD_Rate" : staticUSDRate[0], "USD_Pledged" : USDPledged[0], "Category" : category[0]}
            writer.writerow(projectDict)
print("Done.")
outputfile.close()    
input("Press enter to continue...")