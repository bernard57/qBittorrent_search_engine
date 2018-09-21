#VERSION: 1.4
#AUTHORS: mauricci

from helpers import retrieve_url
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
import re

try:
    #python3
    from html.parser import HTMLParser
except ImportError:
    #python2
    from HTMLParser import HTMLParser
         
class kickass_torrent(object):
    url = 'https://kickass-cr.online'
    name = 'KickAss torrent'
    supported_categories = {'all': 'all'}
    
    class MyHTMLParser(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self.url = 'https://kickass-cr.online'
            self.TABLE_INDEX = 1
            self.insideDataTd = False
            self.tdCount = -1
            self.tableCount = -1
            self.infoMap = {'name':0,'size':1}
            self.fullResData = []
            self.singleResData = self.getSingleData()
            
        def getSingleData(self):
            return {'name':'-1','seeds':'-1','leech':'-1','size':'-1','link':'-1','desc_link':'-1','engine_url':self.url}
        
        def handle_starttag(self, tag, attrs):
            #print("Encountered a start tag:", tag)
            if tag == 'table':
                self.tableCount += 1
            if tag == 'td':
                self.tdCount += 1
                if self.tableCount == self.TABLE_INDEX:
                    self.insideDataTd = True
            if self.insideDataTd and tag == 'a' and len(attrs) > 0:
                 Dict = dict(attrs)
                 if self.infoMap['name'] == self.tdCount and 'href' in Dict \
                    and Dict.get('class','').find('cellMainLink') != -1:
                     self.singleResData['desc_link'] = self.url + Dict['href']
                     self.singleResData['link'] = self.singleResData['desc_link']

        def handle_endtag(self, tag):
            if tag == 'td':
                self.insideDataTd = False
            if tag == 'tr':
                self.tdCount = -1
                if len(self.singleResData) > 0:
                    #ignore trash stuff
                    if self.singleResData['name'] != '-1' and self.isValidSize(self.singleResData['size']) \
                      and not self.singleResData['name'].startswith('Advertising'):
                        prettyPrinter(self.singleResData)
                        self.fullResData.append(self.singleResData)
                    self.singleResData = self.getSingleData()

        def handle_data(self, data):
            if self.insideDataTd:
                for key,val in self.infoMap.items():
                    if self.tdCount == val:
                        currKey = key
                        if currKey in self.singleResData and data.strip() != '':
                            if self.singleResData[currKey] == '-1':
                                self.singleResData[currKey] = data.strip()
                            else:
                                self.singleResData[currKey] += data.strip()

        #true if the size is valid (must contain number and no ',')
        def isValidSize(self, size):
            return size.find(',') == -1 and bool(re.search(r'\d', size))

        #remove who uploaded the torrent
        def adjustName(self):
            for singleData in self.fullResData:
                string = singleData['name']
                if string != '-1':
                    #remove uploaded... from name of torrent
                    index = string.find('Posted by')
                    if index != -1:
                        singleData['name'] = string[:index].strip()


    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        what = what.replace('%20','-')
        currCat = self.supported_categories.get(cat,'all')
        parser = self.MyHTMLParser()

        #analyze firt 10 pages of results
        for currPage in range(1,11):
            url = self.url+'/search/{0}/{1}/'.format(what,currPage)
            html = retrieve_url(url)
            parser.feed(html)
            parser.adjustName()
        #print(parser.fullResData)
        data = parser.fullResData
        parser.close()


    def download_torrent(self, info):
        """ Downloader """
        #KickAss html does not contain tor or magnet link. They are added with javascript

if __name__ == "__main__":
    k = kickass_torrent()
    k.search('tomb%20raider')
