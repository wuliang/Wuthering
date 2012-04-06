#! /bin/sh
# use it to get every day feeding to the brain
rm -f *.db
rm -f *.txt
python wuthering.py rss
python wuthering.py post
python wuthering.py full
python ToolGetText.py 2001-01-01
