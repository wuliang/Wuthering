# -*- coding: utf8 -*-
import re
import sys
import codecs
import urllib2
import cStringIO as StringIO

from lxml import etree
from wutherdb import *

class RssHttp:

    def parseHtml(self, html, encodings):
        
        try:
            # Don't specify the encoding. Let parser decide by itself
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO.StringIO(html), parser)
            return tree
        except:
            for encoding in encodings:
                try:
                    parser = etree.HTMLParser(encoding=encoding)
                    tree = etree.parse(StringIO.StringIO(html), parser)
                    return tree
                except:
                    pass
            raise
        print "parseHtml has error."

    def parseXml(self, xml, encodings):

        try:
            # Don't specify the encoding. Let parser decide by itself
            parser = etree.XMLParser()
            tree = etree.parse(StringIO.StringIO(html), parser)
            return tree
        except:
            for encoding in encodings:
                try:
                    parser = etree.XMLParser(encoding=encoding)
                    tree = etree.parse(StringIO.StringIO(xml), parser)
                    return tree
                except:
                    pass
            raise     
        print "parseXml has error."
        
    def getPage(self,  url):
        file = urllib2.urlopen(url)
        content = file.read()
        file.close()
        return content
    
    def getNewsText(self, news_url, xpath):
        content = self.getPage(news_url)
        tree = self.parseHtml(content)
        for paragraph in tree.xpath(xpath_text):
            yield paragraph.strip()
    

def string_filter(text,  filters):
    for filter in filters:
        text = text.replace(filter, '')
    return text
    
class RssGate_Baidu(): 
    filters = [u'最新',  u'焦点']
    # gbk = (cp936. or GB2312-80)
    codings = ['gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8']
    root = "http://www.baidu.com/search/rss.html"    
    def getSubRss(self):  
        rssall =[]     
        root = self.root
        http = RssHttp()        

        try:
            page = http.getPage(root)
        except:
            print "fail to get page %s" % root
            return rssall
         
        try:
            tree = http.parseHtml(page, self.codings)
        except:
            print "fail to parse page %s" % root
            return rssall
            

        rsslist = tree.xpath('//div[@class="rsslist"]')
        # all return of lxml is list
        for rss in rsslist:
            # must skip fist li, since the content of the rss is combination of low level li 
            lilist = rss.xpath('.//ul/li/ul/li')
            for li in lilist:
                category = li.xpath('./span/text()')
                url = li.xpath('./input[@type="text"]/@value')
                rssall.append((string_filter(category[0],  self.filters), url[0]))
        return rssall

    def removeSubRss(self):
        db = WutherSql("wuther.db")        
        rsslist = db.remove_gate_rsses(self.root)
        db.close()
        
    def recordSubRss(self, rssall):
        db = WutherSql("wuther.db")  
        for category, rss in rssall:
            dbrss = {}
            dbrss['url'] = rss
            dbrss['category'] = category
            dbrss['gate'] = self.root
            db.insert_rss(dbrss)
        db.close()
                
    def fetchSubRss(self):
        db = WutherSql("wuther.db")        
        rsslist = db.fetch_gate_rsses(self.root)         
        db.close()
        return rsslist

    def run4rss(self):
        rssall = self.getSubRss()
        if rssall:
        # replace with newest data
            self.removeSubRss()
            self.recordSubRss(rssall)        
    
    
class RssEntry_Baidu():
    filters = [u'最新',  u'焦点']
    codings = ['gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8']
    paralen = 30
    maxfetch = 5
    def __init__(self,  url):
        self.url = url
                        
    def getItems(self,  category):
        itemall =[]
        root = self.url
        http = RssHttp()    
        try:
            page = http.getPage(root)
        except:
            print "fail to get page %s" % root
            return itemall

        try:
            tree = http.parseXml(page,  self.codings)
        except:
            print "fail to parse page %s" % root
            return itemall 
            
        channels = tree.xpath('//channel')
        # all return of lxml is list
        for channel in channels:
            titles = channel.xpath('.//title')
            chtitle = titles[0]
            items = channel.xpath('.//item')
            for item in items:
                oneitem = {}
                # print etree.tostring(item) (good for debug)
                title = item.xpath('./title/text()')
                link = item.xpath('./link/text()')
                pubdate = item.xpath('./pubDate/text()')
                source = item.xpath('./source/text()')
                author = item.xpath('./author/text()')
                description = item.xpath('./description/text()')
                
                if title:
                    oneitem['title'] = title[0]
                if link:    
                    oneitem['url'] =  link[0]
                if pubdate:
                    oneitem['date'] = pubdate[0]
                if source:
                    oneitem['source'] = source[0]
                if author:
                    oneitem['author'] = author[0]
                if description:
                    oneitem['description'] =  self.rss_description_format(description[0])
                
                oneitem['xpath'] = 'NOT KNOWN' 
                oneitem['content'] = 'NOT KNOWN'
                oneitem['category'] = category
                itemall.append(oneitem)
        return itemall

    @staticmethod
    def rss_description_format(text):
        idx = text.find("...<br")
        if idx == -1:
            idx = text.find("<br")
            if idx == -1:
                return "bad format of description"
        text = text[0:idx]
        text= re.sub('[ \t\n\r]', '', text)
        return text

    @staticmethod
    def full_text_format(text):
        text= re.sub('[ \t\n\r]', '', text)
        return text
        
    @staticmethod
    def recordPost(itemall):
        db = WutherSql("wuther.db")  
        for item in itemall:
            db.insert_post(item)
        db.close()
        
    @staticmethod
    def fetch_unfetched_posts():

        db = WutherSql("wuther.db") 
        http = RssHttp()        
        count  = 0
        for item in db.fetch_unfetched_posts():
            root = item['url']
            desp = item['description']
            upt = {}
            upt['fetchdate'] = time.strftime('%Y-%m-%d %H:%M:%S')
            if 'fetcherrnum' not  in item.keys():
                upt['fetcherrnum'] = 1
            else:
                if item['fetcherrnum'] == None:
                    item['fetcherrnum'] = 0
                upt['fetcherrnum'] = item['fetcherrnum'] + 1
             
            if upt['fetcherrnum'] > RssEntry_Baidu.maxfetch:
                db.remove_post(item['id'],  item)
                continue
                
#            count = count + 1
#            if count > 5:
#                break
            try:
                page = http.getPage(root)
            except:
                print "fail to get page %s" % root
                db.update_post(item['id'],  upt)                
                continue

            try:
                tree = http.parseHtml(page, RssEntry_Baidu.codings)
            except:
                print "fail to parse page %s" % root
                db.update_post(item['id'],  upt)                   
                continue
                           
            texts = tree.xpath('//p/text()')

            fulltext=""
            for text in texts:
                if len(text) < RssEntry_Baidu.paralen:
                    continue
                tt = RssEntry_Baidu.full_text_format(text)
                fulltext = fulltext + tt
            
            if len(fulltext) > 2 * RssEntry_Baidu.paralen:
                upt['content'] = fulltext
                db.update_post(item['id'],  upt) 

        db.close()


def run4rss():
    gate  = RssGate_Baidu()
    gate.run4rss()      

def run4newpost():
    gate  = RssGate_Baidu()    
    postlist = []
    for rss in gate.fetchSubRss():    
        rsse = RssEntry_Baidu(rss['url'])
        posts = rsse.getItems(rss['category'])
        postlist.extend(posts)
    RssEntry_Baidu.recordPost(postlist)

def run4fulltext():
    RssEntry_Baidu.fetch_unfetched_posts()
    
def main():
    if len(sys.argv) != 2:
        print "Usage:",  sys.argv[0],  "rss | post | full"
        print "\trss - fetch all the rss address of different categories" 
        print "\tpost - fetch html information from rss flles"
        print "\tfull - fetch full text the the news from website" 
        return
        
    command = sys.argv[1]
    if command == 'rss':
        run4rss()
    elif command == 'post':
        run4newpost()
    elif command == 'full':
        run4fulltext()
    print 'Done.'

if __name__ == '__main__':
    main()
