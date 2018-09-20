#VERSION: 1.2
#AUTHORS: mauricci

from helpers import retrieve_url
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter

try:
    #python3
    from html.parser import HTMLParser
except ImportError:
    #python2
    from HTMLParser import HTMLParser
    
class corsaroblu(object):
    url = 'https://www.ilcorsaroblu.org'
    name = 'Il Corsaro Blu'
    #13%3B14%3B15%3B25%3B17%3B11%3B21 = 13;14;15;25;17;11;21
    supported_categories = {'all': '0', 'movies': '13%3B14%3B15%3B25%3B17%3B11%3B21', 'tv': '19%3B20%3B24', 'music': '2', 'games': '3'}
    
    class MyHTMLParser(HTMLParser):
    
        def __init__(self):
            HTMLParser.__init__(self)
            self.url = 'https://www.ilcorsaroblu.org'
            self.insideTd = False
            self.insideDataTd = False
            self.tableFound = False
            self.tdCount = -1
            self.infoMap = {'name':1,'torrLink':3,'size':9,'seeds':6,'leech':7}
            self.fullResData = []
            self.singleResData = self.getSingleData()

        def getSingleData(self):
            return {'name':'-1','seeds':'-1','leech':'-1','size':'-1','link':'-1','desc_link':'-1','engine_url':self.url}
        
        def handle_starttag(self, tag, attrs):
            if tag == 'td':
                self.insideTd = True
                Dict = dict(attrs)
                if Dict.get('class','').find('lista') != -1:
                    self.insideDataTd = True
                    self.tdCount += 1
            if self.tableFound and self.insideTd and tag == 'a' and len(attrs) > 0:
                 Dict = dict(attrs)
                 if self.infoMap['torrLink'] == self.tdCount and 'href' in Dict:
                     self.singleResData['link'] = 'https://www.ilcorsaroblu.org/' + Dict['href']
                 if self.infoMap['name'] == self.tdCount and 'href' in Dict:
                     self.singleResData['desc_link'] = 'https://www.ilcorsaroblu.org/' + Dict['href']

        def handle_endtag(self, tag):
            if tag == 'table':
                self.tableFound = False
            if tag == 'td':
                self.insideTd = False
                self.insideDataTd = False
            if tag == 'tr':
                self.tdCount = -1
                if len(self.singleResData) > 0:
                    #ignore trash stuff
                    if self.singleResData['name'] != '-1' and self.singleResData['size'].find(',') == -1:
                        #ignore those with link and desc_link equals to -1
                        if (self.singleResData['desc_link'] != '-1' or self.singleResData['link'] != '-1') \
                           and self.singleResData['link'] != self.singleResData['desc_link']:
                            prettyPrinter(self.singleResData)
                            self.fullResData.append(self.singleResData)
                    self.singleResData = self.getSingleData()

        def handle_data(self, data):     
            if self.insideTd:
                if data.strip().startswith('Torrents Added'):
                    self.tableFound = True
            if self.insideDataTd and self.tableFound:        
                if self.tableFound:    
                    for key,val in self.infoMap.items():
                        if self.tdCount == val:
                            currKey = key
                            if currKey in self.singleResData and data.strip() != '':
                                if self.singleResData[currKey] == '-1':
                                    self.singleResData[currKey] = data.strip()
                                else:
                                    self.singleResData[currKey] += data.strip()


    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        #if user provides wrong category, let's search with the default category
        currCat = self.supported_categories.get(cat, self.supported_categories['all'])
        parser = self.MyHTMLParser()

        #analyze firt 10 pages of results
        for currPage in range(1,11):
            url = self.url+'/index.php?page=torrents&search={0}&category={1}&pages={2}'.format(what,currCat,currPage)
            #print(url)
            html = retrieve_url(url)
            parser.feed(html)
        #print(parser.fullResData)
        data = parser.fullResData
        parser.close()


    def download_torrent(self, info):
            """ Downloader """
            print(download_file(info))

if __name__ == "__main__":
    c = corsaroblu()
    c.search('tomb%20raider')
