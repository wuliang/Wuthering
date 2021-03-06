# -*- coding: utf8 -*-
import sys
import time
import codecs
from wutherdb import *

def main():
    if len(sys.argv) < 2:
        print "Usage:",  sys.argv[0],  "starttime [endtime]"
        print r"Time format is '%Y-%m-%d %H:%M:%S'"
        return
        
    starttime = sys.argv[1]
    if len(sys.argv) >= 3:
        endtime = sys.argv[2]
    else:
        endtime = time.strftime('%Y-%m-%d %H:%M:%S')
    
    
    # if the file name is not required to be readable
    #import base64
    #file_name_string = base64.urlsafe_b64encode(your_string)
    import string
    filename = "From%sTo%s.txt" % (starttime,  endtime)
    safechars = '_-.()' + string.digits + string.ascii_letters
    filename = "".join([x for x in filename if x in safechars])

    file = codecs.open(filename, 'wt', encoding='utf8')
    if not file:
        return
    db = WutherSql("wuther.db")
    
    # Sorry, the format of post time may be changed (in Rss Gate)
    # rows = db.fetch_duration_posts(starttime,  endtime)  
    rows = db.fetch_duration_posts_by_fetchtime(starttime,  endtime) 
    
    for row in rows:        
        print >>file, row['content']
        print >>file, "\n\n\n"
    print "%d posts has been copied to file %s" % (len(rows),  filename)


if __name__ == "__main__":
    main()
    
