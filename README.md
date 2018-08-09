# Now/Here  

Simple browser-based note-taking.
- tagging
- full-text search
- location aware
- stores diffs
- uses Flask / Mongo / nginx

Test/develop with `./main.py`  

Deploy behind nginx with `./launch.sh`   


### todo

Notes.app pull (when note is older than a week)
tool to normalize tags (what, is it 2004?)

Applescript is slow as shit
2739 / 1.5s
~30 minutes to run once


### install

brew install mongodb  
brew install uwsgi  
pip3 install flask  
pip3 install uwsgi  
pip3 install pymongo  
pip3 install diff-match-patch  
pip3 install requests  
pip3 install pillow  
pip3 install PyYAML  
pip3 install python-geohash  
pip3 install dateutil  
pip3 install pytz  

### server

/usr/local/etc/nginx/nginx.conf 
/usr/local/etc/mongod.conf

brew services restart nginx
brew services restart mongodb


### ref

https://gist.github.com/mplewis/6076082