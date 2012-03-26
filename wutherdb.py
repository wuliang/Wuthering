# -*- coding: utf8 -*-
import collections
import logging
import math
import os
import random
import re
import sqlite3
import time
import types

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def dict_show(myDict):
    print '-' * 80
    for key in myDict.keys():
        print key, ' : ',  myDict[key]    

class WutherSql:
    """Database functions to support a Cobe brain. This is not meant
    to be used from outside."""
    def __init__(self, filename):
        if not os.path.exists(filename):
            self.init(filename)

        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = dict_factory
        self.insert_errnum = 0
        self.update_errnum = 0
        self.remove_errnum = 0
        
    def commit(self):
        ret = self.conn.commit()
        return ret
        
    def close(self):
        
        self.conn.cursor().close()
        self.conn.close()

    # myDict is used for reference 
    def remove_dict(self,  table,  id, myDict):
        c = self.conn.cursor()
        try:
            qry = "DELETE FROM %s WHERE id=%s" % (table, id)
            c.execute(qry, ())               
            self.commit()
        except sqlite3.IntegrityError:
            #print "in table %s, a update dict error occur" % table 
            #dict_show(myDict)
            self.remove_errnum = self.remove_errnum + 1
       
    def remove_post(self,  id, post):
        self.remove_dict("post", id,  post)
        return        

    def remove_website(self, id,  website):
        self.remove_dict("rss",  id, website)        
        return
        
    def remove_rss(self, id,  rss):
        self.iremove_dict("rss", id,  rss)        
        return
        
    def update_dict(self,  table,  id,  myDict):
        c = self.conn.cursor()
        kmarks = '=?, '.join(myDict.keys())
        kmarks = kmarks + '=?'
        try:
            qry = "UPDATE %s SET %s WHERE id=%s" % (table, kmarks, id)
            c.execute(qry, myDict.values())               
            self.commit()
        except sqlite3.IntegrityError:
            #print "in table %s, a update dict error occur" % table 
            #dict_show(myDict)
            self.update_errnum = self.update_errnum + 1
       
    def update_post(self,  id, post):
        self.update_dict("post", id,  post)
        return        

    def update_website(self, id,  website):
        self.update_dict("rss",  id, website)        
        return
        
    def update_rss(self, id,  rss):
        self.iupdate_dict("rss", id,  rss)        
        return
        
    def insert_dict(self,  table,  myDict):
        c = self.conn.cursor()
        
        qmarks = ', '.join('?' * len(myDict))
        kmarks = ', '.join(myDict.keys())
        try:
            qry = "Insert Into %s (%s) Values (%s)" % (table, kmarks, qmarks)
            c.execute(qry, myDict.values())               
            self.commit()
        except sqlite3.IntegrityError:
            #print "in table %s, a duplicate insertion is found" % table 
            #dict_show(myDict)
            self.insert_errnum = self.insert_errnum + 1
                
    def insert_post(self,  post):
        self.insert_dict("post",  post)
        return        

    def insert_website(self,  website):
        self.insert_dict("rss",  website)        
        return
        
    def insert_rss(self,  rss):
        self.insert_dict("rss",  rss)        
        return
        
    def fetch_unfetched_posts(self):

        c = self.conn.cursor()
        q = "SELECT * FROM post WHERE content = 'NOT KNOWN' "
        rows = c.execute(q, ()).fetchall()
        return rows
        
    def fetch_cat_duration_posts(self, category, old,  new):

        c = self.conn.cursor()
        q = "SELECT * FROM post WHERE date < ? AND date > ? AND category = ?"
        rows = c.execute(q, (new, old, category)).fetchall()
        return rows
        
    def fetch_duration_posts(self, old,  new):

        c = self.conn.cursor()
        q = "SELECT * FROM post WHERE date < ? AND date > ?"
        rows = c.execute(q, (new, old)).fetchall()
        return rows
        
    def fetch_category_posts(self, category):

        c = self.conn.cursor()
        q = "SELECT * FROM post WHERE category = ?"
        rows = c.execute(q, (category, )).fetchall()
        return rows
        
    def fetch_posts(self):

        c = self.conn.cursor()
        q = "SELECT * FROM post"
        rows = c.execute(q, ()).fetchall()
        return rows

    def fetch_rsses(self):
        
        c = self.conn.cursor()
        q = "SELECT * FROM rss"
        rows = c.execute(q, ()).fetchall()
        return rows
    
    def fetch_gate_rsses(self,  gate):
        
        c = self.conn.cursor()
        q = "SELECT * FROM rss WHERE gate = ?"
        rows = c.execute(q, (gate, )).fetchall()
        return rows
    
    def remove_gate_rsses(self,  gate):
        c = self.conn.cursor()
        q = "DELETE FROM rss WHERE gate = ?"
        ret = c.execute(q, (gate, ))
        self.commit()
        return ret
        
    def fetch_websites(self):
        
        c = self.conn.cursor()
        q = "SELECT * FROM website"
        rows = c.execute(q, ()).fetchall()
        return rows
        
        
    def init(self, filename):
        self.conn = sqlite3.connect(filename)
        c = self.conn.cursor()    
        c.execute("""
        CREATE TABLE rss (
         id INTEGER  PRIMARY KEY AUTOINCREMENT,
         url STRING UNIQUE NOT NULL,
         category STRING,
         gate STRING       
        ) """    )
  
        c.execute("""
        CREATE INDEX rss__url ON rss (url)
        """) 
     
        c.execute("""   
        CREATE TABLE website (
         id INTEGER  PRIMARY KEY AUTOINCREMENT,
         url STRING UNIQUE NOT NULL,
         rss STRING       
        ) """    )
  
        c.execute("""
        CREATE INDEX website__url ON website (url)
        """) 
        
        c.execute("""
        CREATE TABLE post (
         id INTEGER  PRIMARY KEY AUTOINCREMENT,
         url STRING UNIQUE NOT NULL,
         title STRING, 
         category STRING,
         source STRING, 
         author STRING,
         description STRING, 
         fetchdate datetime,
         fetcherrnum  INTEGER,
         date datetime NOT NULL,
         xpath STRING NOT NULL,         
         content TEXT NOT NULL
        ) """   )

        c.execute("""
        CREATE INDEX post__url ON post (url)
        """) 

        self.commit()
        self.close()

def main():
    db = WutherSql("wuther.db")
    post = {}
    post["xpath"] = "USA AM COMING"
    post["url"] = "USA AM URL"
    post["category"] = "CHINA"
    post["date"] = time.strftime('%Y-%m-%d %H:%M:%S')
    post["content"] = "BALABALBALABABALA,,,,,,,"
   # print **(post.values())
    db.insert_post(post)
    #rows = db.fetch_category_posts("CHINA")
    rows = db.fetch_cat_duration_posts("CHINA","2012-03-25 22:27:21",  "2032-03-25 22:27:29")    
    for row in rows:
        print row
        
if __name__ == "__main__":
    main()
