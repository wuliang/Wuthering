# -*- coding: utf8 -*-
import re
import sys
import cookielib
import codecs
import urllib2
import cStringIO as StringIO

from lxml import etree
from wutherdb import *
from wuthertest import *

def lxml_node_text(node):
    if node.text:
        result = node.text
    else:
        result = ''
    for child in node:
        if child.tail is not None:
            result += child.tail
    return result
    
class RssHttp:

    def parse_html_basic(self,  html,  encoding):
        parser = etree.HTMLParser(encoding=encoding)
        tree = etree.parse(StringIO.StringIO(html), parser)
        return tree

    def parse_xml_basic(self, xml, encoding):
        parser = etree.XMLParser(encoding=encoding)
        tree = etree.parse(StringIO.StringIO(xml), parser)
        return tree
                    
    def parseHtml(self, html, encodings):
        
        try:
            # Don't specify the encoding. Let parser decide by itself
            parser = etree.HTMLParser(encoding=None)
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
            return None
        print "parseHtml has error."

    def parseXml(self, xml, encodings):

        try:
            # Don't specify the encoding. Let parser decide by itself
            parser = etree.XMLParser(encoding=None)
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
            return None     
        print "parseXml has error."
    
           
    def getPage(self,  url):

        try:
            file = urllib2.urlopen(url, None, 5)
        except:
            print "Socket %s timed out!" % url
            return None
        try:
            content = file.read()
        except:
            print "Socket %s timed out!" % url
            file.close()
            return None
            
        file.close()
        return content
    
    def getNewsText(self, news_url, xpath_text):
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

        
        page = http.getPage(root)
        if not page:
            print "fail to get page %s" % root
            return rssall
         
        tree = http.parseHtml(page, self.codings)
        if not tree:
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
    maxfetch = 3
    def __init__(self,  url):
        self.url = url
                        
    def getItems(self,  category):
        itemall =[]
        root = self.url
        http = RssHttp()    
        page = http.getPage(root)
        if not page:
            print "fail to get page %s" % root
            return itemall

        tree = http.parseXml(page,  self.codings)
        if not tree:
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
        # this contain three types of space
        text= re.sub('[ \t\n\r]+', '', text)
        return text
        
    @staticmethod
    def recordPost(itemall):
        db = WutherSql("wuther.db")  
        for item in itemall:
            db.insert_post(item)
        db.close()
    
    @staticmethod
    def extrace_text_local(http, page):
        codings = [None]
        xpaths = ['//div[@id="p_content"]',  '//div[@id="contentText"]', '//p' ]
        codings.extend(RssEntry_Baidu.codings)
        for code in codings:
            try:
                tree = http.parse_html_basic(page, code)
                for xpath in xpaths:
                    #print code,  xpath
                    try:
                        nodes = tree.xpath(xpath)
                        if not nodes:
                            continue                
                    
                        fulltext=""
                        for node in nodes:
                            text = lxml_node_text(node)
                            if len(text) < RssEntry_Baidu.paralen:
                                continue
                            tt = RssEntry_Baidu.full_text_format(text)
                            fulltext = fulltext + tt
                
                        if len(fulltext) > 2 * RssEntry_Baidu.paralen:
                            return fulltext
                    except:
                        pass
            except:
                pass
        return None
                
    @staticmethod
    def fetch_unfetched_posts():

        db = WutherSql("wuther.db") 
        http = RssHttp()        
        count  = 0
        success = 0
        todo = db.fetch_unfetched_posts()
        total = len(todo)
        for item in todo:

            count = count + 1
                          
            root = item['url']
            desp = item['description']
            content = item['content']
            if 'fetcherrnum' not  in item.keys() or not item['fetcherrnum']:
                item['fetcherrnum'] = 0
            sys.stdout.write(" " * 80)
            sys.stdout.write('\r[%d/%d/%d] process %s  ...  %s , %d' % (count, success,  total,  root,  content,  item['fetcherrnum']))
            sys.stdout.flush()
            
            upt = {}
            upt['fetchdate'] = time.strftime('%Y-%m-%d %H:%M:%S')
            upt['fetcherrnum'] = item['fetcherrnum'] + 1
             
            if upt['fetcherrnum'] > RssEntry_Baidu.maxfetch:
                db.remove_post(item['id'],  item)
                continue                
            
            page = http.getPage(root)
            if not page:
                sys.stdout.write("fail to get page")
                db.update_post(item['id'],  upt)                
                continue

            content = RssEntry_Baidu.extrace_text_local(http, page)
            if not content:
                sys.stdout.write("fail to parse page")
                db.update_post(item['id'],  upt)                   
                continue
            
            upt['content'] = content
            db.update_post(item['id'],  upt) 
            
            success = success + 1
            
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
    elif command == 'test':
        run4test()        
    print 'Done.'

if __name__ == '__main__':
    main()
