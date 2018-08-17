from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen
import urllib.request as ul
from urllib.parse import urlparse, urljoin
import re
import time
from Blacklists import BLACKLIST, INVALID_TYPES 


class DomainFinder:
    R_DEPTH = 3
    currentCountry = "Test"
    linkSet = set()
        
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    
    
    
    # Generates list of all links on a webpage
    def getlinks(self, url):
        # Stores page's html as object
        request = ul.Request(url, headers=self.hdr)
        page = urlopen(request) 
        # ga_tag = SoupStrainer('a')
        soup = BeautifulSoup(page, 'lxml', parse_only = SoupStrainer('a'))
        urls = []
        # Parses all urls into list
        for anchor in soup.findAll('a', href=True):
            linkDict = {'Country': "", 'URL': "", 'Title': "", 'Year' : "", 'Document Type' : "" }
            linkDict['Title'] = anchor.string
            link = anchor.get('href')
            if not(link.startswith('http')):
                link = urljoin(url, link)
            linkDict['URL'] = link
            urls.append(linkDict)
        return urls
    
    
    # Parses all internal domain links into a list
    def get_internal_domains(self, url, r_level, visited, pdflinks):
        print(str(url) + ": " + str(r_level))
        visited.add(url)
        parsed_uri = urlparse(url)
        # Parses domain substring
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        # Generates list of all links
        try:
            urls = self.getlinks(url)
            unvisited_domains = []
            for linkDict in urls:
                if(('.pdf' in str(linkDict["URL"]) or '.PDF' in str(linkDict["URL"])) and not(str(linkDict["URL"]) in self.linkSet)):
                    self.linkSet.add(linkDict['URL'])
                    pdflinks.append(linkDict)
                elif ((domain in linkDict['URL']) and self.linkValid(linkDict['URL']) and not(linkDict['URL'] in visited)):
                    unvisited_domains.append(linkDict['URL'])
            print(unvisited_domains)
            if ((not unvisited_domains) or (r_level == self.R_DEPTH)):
                print("REACHED LIMIT")
                return pdflinks
            else:
                for link in unvisited_domains:
                    if not(link in visited):
                        time.sleep(3)
                        self.get_internal_domains(link, r_level+1, visited, pdflinks)
        except KeyboardInterrupt:
            print(pdflinks)
            raise
        except Exception as e:
            print(e)
            pass
        return pdflinks           
        #return internal_domains
    
    def linkValid(self, link):
        if ((not self.blacklisted(link,BLACKLIST)) and self.validType(link)):
            return True
        else:
            return False
    
    def blacklisted(self,link, blacklist):
        for banned_domain in blacklist:
            if banned_domain in link:
                return True
        return False
    
    def validType(self,link):
        urlTokens = link.split('.')
        if(('.' + urlTokens[-1]) in INVALID_TYPES):
            return False
        else:
            return True
    
    # For each webpage, get links to list, filter for doamin and store relevant links in key-value pair of (Domina: [relevant links]
    def test(self,_url):
        str(time.strftime("%I:%M:%S"))
        #print(getlinks(_url))
        dictList = self.get_internal_domains(_url, 0, set(), [])
        for d in dictList:
            print(d)
        #print(visited)
        print("\n\n-----------------------------------------------\n\n")
        str(time.strftime("%I:%M:%S"))
        print("Done")


df = DomainFinder()
#df.test("https://www.bankofengland.co.uk/")
print(df.getlinks("https://www.kickstarter.com/discover/advanced?term=luxembourg&woe_id=0&sort=end_date&seed=2554907&page=2"))
input("Press Enter to continue...")