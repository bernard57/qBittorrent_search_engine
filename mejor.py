#VERSION: 1.0
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
    
class mejor(object):
    url = 'http://www.mejortorrent.org'
    name = 'MejorTorrent'
    supported_categories = {'all': '0'}
    
    class MyHTMLParser(HTMLParser):

        def getSingleData(self):
            return {'name':'-1','seeds':'-1','leech':'-1','size':'-1','link':'-1','desc_link':'-1','engine_url':'MejorTorrent',}

        insideTd = False
        insideDataTd = False
        tableCount = -1
        tdCount = -1
        infoMap = {'name': 0}
        fullResData = []
        singleResData = getSingleData(None)
        
        def handle_starttag(self, tag, attrs):
            if tag == 'table':
                self.tableCount += 1
            if tag == 'td':
                self.insideTd = True
                Dict = dict(attrs)
                if self.tableCount == 15:
                    self.insideDataTd = True
                    self.tdCount += 1
            if self.insideDataTd and tag == 'a' and len(attrs) > 0:
                 Dict = dict(attrs)
                 if self.infoMap['name'] == self.tdCount and 'href' in Dict:
                     self.singleResData['desc_link'] = 'http://www.mejortorrent.org' + Dict['href']
                     self.singleResData['link'] = self.singleResData['desc_link']

        def handle_endtag(self, tag):
            if tag == 'td':
                self.insideTd = False
                self.insideDataTd = False
            if tag == 'tr':
                self.tdCount = -1
                if len(self.singleResData) > 0:
                    #ignore trash stuff
                    if self.singleResData['name'] != '-1':
                        #ignore those with link and desc_link equals to -1
                        if (self.singleResData['desc_link'] != '-1' or self.singleResData['link'] != '-1'):
                            prettyPrinter(self.singleResData)
                            self.fullResData.append(self.singleResData)
                    self.singleResData = self.getSingleData()

        def handle_data(self, data):
            if self.insideDataTd:
                #print(data)
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

        #analyze firt pages of results (it should list all results)
        for currPage in range(1,2):
            url = self.url+'/secciones.php?sec=buscador&valor={0}'.format(what)
            #print(url)
            html = retrieve_url(url)
            parser.feed(html)
        #print(parser.fullResData)
        data = parser.fullResData
        parser.close()


    def download_torrent(self, info):
            """ Downloader """
            html = retrieve_url(info)
            m = re.search('(<a.*?>Descargar</a>)', html)
            if m is not None and m.group(1) is not None:
                torrentAnchor = m.group(1)
                torrentLink1 = re.search('href=[\'\"](.+?)[\'\"]',torrentAnchor)
                if torrentLink1 is not None and torrentLink1.group(1) is not None:
                    torrentUrl = self.url + '/' + torrentLink1.group(1)
                    html = retrieve_url(torrentUrl)
                    torrentLink2 = re.search('<a.*?href=[\'\"](.+?\.torrent)[\'\"]>',html)
                    if torrentLink2 is not None and torrentLink2.group(1) is not None:
                        #download_file is tested and downloads correctly the .torrent file
                        #starting from the desc_url from the torrent choosen. Anyway qBittorrent won't download anything
                        print(download_file(torrentLink2.group(1)))

if __name__ == "__main__":
    m = mejor()
    m.search('tomb%20raider')