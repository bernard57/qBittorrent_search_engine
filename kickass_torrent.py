#VERSION: 1.1
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
         
class kickass_torrent(object):
    url = 'https://kickass-cr.online'
    name = 'KickAss torrent'
    supported_categories = {'all': 'all', 'movies': 'movies', 'tv': 'tv', 'music': 'music', 'games': 'games'}
    
    class MyHTMLParser(HTMLParser):

        def getSingleData(self):
            return {'name':'-1','seeds':'-1','leech':'-1','size':'-1','link':'-1','desc_link':'-1','engine_url':'KickAss',}

        insideTd = False
        tableFound = False
        tdCount = -1
        infoMap = [('name',0),('size',1),('seeds',4),('leech',5)]
        fullResData = []
        singleResData = getSingleData(None)
        
        def handle_starttag(self, tag, attrs):
            #print("Encountered a start tag:", tag)
            if tag == 'table':
                self.tableFound = True
            if self.tableFound and tag == 'td':
                self.tdCount += 1
                self.insideTd = True
            if self.tableFound and tag == 'a' and len(attrs) > 0:
                 Dict = dict(attrs)
                 if Dict.get('class','').find('cellMainLink') != -1 and 'href' in Dict:
                     self.singleResData['desc_link'] = 'https://kickass-cr.online' + Dict['href']
                 if 'href' in Dict and Dict['href'].find('magnet') != -1:
                     self.singleResData['link'] = Dict['href']

        def handle_endtag(self, tag):
            if tag == 'table':
                self.tableFound = False
            if tag == 'td':
                self.insideTd = False
            if tag == 'tr':
                self.tdCount = -1
                if len(self.singleResData) > 0:
                    self.fullResData.append(self.singleResData)
                    #ignore trash stuff
                    if self.singleResData['name'] != '-1' and self.singleResData['size'].find(',') == -1 \
                      and not self.singleResData['name'].startswith('Advertising'):
                        prettyPrinter(self.singleResData)
                    self.singleResData = self.getSingleData()

        def handle_data(self, data):
            if self.insideTd:
                for Tuple in self.infoMap:
                    if self.tdCount == Tuple[1]:
                        currKey = Tuple[0]
                        if data.strip() != '':
                            if self.singleResData[currKey] == '-1':
                                self.singleResData[currKey] = data.strip()
                            else:
                                self.singleResData[currKey] += data.strip()

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
        currCat = self.supported_categories.get(cat,'all')
        parser = self.MyHTMLParser()

        #analyze firt 10 pages of results
        for currPage in range(1,11):
            url = self.url+'/usearch/{0}%20category:{1}/{2}/?field=seeders&sorder=desc'.format(what,currCat,currPage)
            html = retrieve_url(url)
            parser.feed(html)
            parser.adjustName()
        #print(parser.fullResData)
        data = parser.fullResData
        parser.close()


    def download_torrent(self, info):
            """ Downloader """
            print(download_file(info))

if __name__ == "__main__":
    k = kickass_torrent()
    k.search('tomb%20raider')
