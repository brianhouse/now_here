# Now/Here  

Simple browser-based note-taking.
- tagging
- full-text search
- location aware
- stores diffs
- uses Flask / Mongo / nginx

Test/develop with `./main.py`  

Deploy behind nginx with `./launch.sh`   


### bugs

applescript on Notes.app is pretty broken in Catalina. delete function doesn't work


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
pip3 install boto3

### server

/usr/local/etc/nginx/nginx.conf  
/usr/local/etc/mongod.conf  

brew services restart nginx  
brew services restart mongodb  


### ref

https://gist.github.com/mplewis/6076082
