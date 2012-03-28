# -*- coding: utf8 -*-
import re
import sys
import cookielib
import codecs
import urllib2
import cStringIO as StringIO

from lxml import etree
from wutherdb import *
from wuthering import *

def run4test_ok1(): 
    root = "http://www.wzrb.com.cn/article362343show.html"
    http = RssHttp()      
    page = http.getPage(root)
    #tree = http.parseHtml(page, RssEntry_Baidu.codings)
    #'gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8'
    parser = etree.HTMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(page), parser)
    if not tree:
        print "fail to parse page %s" % root
        return
    
    #print etree.tostring(tree)    
    texts = tree.xpath('//p/text()')
    fulltext=""
    for text in texts:
        #print etree.tostring(text)
        if len(text) < RssEntry_Baidu.paralen:
            continue
        tt = RssEntry_Baidu.full_text_format(text)
        fulltext = fulltext + tt
    
    if len(fulltext) > 2 * RssEntry_Baidu.paralen:
        print  "OK"
    
    print fulltext
        


    
def run4test_ok2(): 
    root = "http://notebook.yesky.com/358/31043858.shtml"
    http = RssHttp()
    page = http.getPage(root)
    #tree = http.parseHtml(page, RssEntry_Baidu.codings)
    #'gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8'
    parser = etree.HTMLParser(encoding='gb18030')
    tree = etree.parse(StringIO.StringIO(page), parser)
    if not tree:
        print "fail to parse page %s" % root
        return
    
    #print etree.tostring(tree)    
    
    nodes = tree.xpath('//p')
    fulltext=""
    for node in nodes:
        text = lxml_node_text(node)
        #print etree.tostring(text)
        if len(text) < RssEntry_Baidu.paralen:
            continue
        tt = RssEntry_Baidu.full_text_format(text)
        fulltext = fulltext + tt
    
    if len(fulltext) > 2 * RssEntry_Baidu.paralen:
        print  "OK"
    
    print fulltext
        

def run4test_ok3(): 
    root = "http://news.bangkaow.com/news/20120323/340351.html"
    http = RssHttp()
    page = http.getPage(root)
    #tree = http.parseHtml(page, RssEntry_Baidu.codings)
    #'gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8'
    parser = etree.HTMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(page), parser)
    if not tree:
        print "fail to parse page %s" % root
        return
    
    #print etree.tostring(tree)    
    
    nodes = tree.xpath('//p')
    fulltext=""
    for node in nodes:
        text = lxml_node_text(node)
        #print etree.tostring(text)
        if len(text) < RssEntry_Baidu.paralen:
            continue
        tt = RssEntry_Baidu.full_text_format(text)
        fulltext = fulltext + tt
    
    if len(fulltext) > 2 * RssEntry_Baidu.paralen:
        print  "OK"
    
    print fulltext
    
def run4test_ok4(): 
    root = "http://news.cjn.cn/sywh/201203/t1722548.htm"
    http = RssHttp()
    page = http.getPage(root)
    #tree = http.parseHtml(page, RssEntry_Baidu.codings)
    #'gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8'
    parser = etree.HTMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(page), parser)
    if not tree:
        print "fail to parse page %s" % root
        return
    
    #print etree.tostring(tree)    
    
    nodes = tree.xpath('//p')
    fulltext=""
    for node in nodes:
        text = lxml_node_text(node)
        #print etree.tostring(text)
        if len(text) < RssEntry_Baidu.paralen:
            continue
        tt = RssEntry_Baidu.full_text_format(text)
        fulltext = fulltext + tt
    
    if len(fulltext) > 2 * RssEntry_Baidu.paralen:
        print  "OK"
    
    print fulltext
    
def run4test_fail1(): 
    root = "http://ent.xinmin.cn/2012/03/27/14184346.html"
    http = RssHttp()
    page = http.getPage(root)
    #tree = http.parseHtml(page, RssEntry_Baidu.codings)
    #'gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8'
    parser = etree.HTMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(page), parser)
    if not tree:
        print "fail to parse page %s" % root
        return
    
    #print etree.tostring(tree)    
    
    nodes = tree.xpath('//p')
    fulltext=""
    for node in nodes:
        text = lxml_node_text(node)
        #print etree.tostring(text)
        if len(text) < RssEntry_Baidu.paralen:
            continue
        tt = RssEntry_Baidu.full_text_format(text)
        fulltext = fulltext + tt
    
    if len(fulltext) > 2 * RssEntry_Baidu.paralen:
        print  "OK"
    
    print fulltext
    
    
def run4test_fail2(): 
    root = "http://ent.qq.com/a/20120326/001192.html"
    http = RssHttp()
    page = http.getPage(root)
    content = RssEntry_Baidu.extrace_text_local(http, page)
    if not content:
        print("fail to parse page")
    else:
        print content


def run4test(): 
    root = "http://news.bangkaow.com/news/20120323/340351.html"
    http = RssHttp()
    page = http.getPage(root)
    #tree = http.parseHtml(page, RssEntry_Baidu.codings)
    #'gb2312',  'gbk', 'cp1252', 'gb18030', 'utf8'
    parser = etree.HTMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(page), parser)
    if not tree:
        print "fail to parse page %s" % root
        return
    
    #print etree.tostring(tree)    
    
    nodes = tree.xpath('//p')
    fulltext=""
    for node in nodes:
        text = lxml_node_text(node)
        #print etree.tostring(text)
        if len(text) < RssEntry_Baidu.paralen:
            continue
        tt = RssEntry_Baidu.full_text_format(text)
        fulltext = fulltext + tt
    
    if len(fulltext) > 2 * RssEntry_Baidu.paralen:
        print  "OK"
    
    print fulltext
