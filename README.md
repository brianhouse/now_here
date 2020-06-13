# Now/Here  

Simple browser-based note-taking.
- tagging
- full-text search
- location aware
- stores diffs
- uses Flask / Mongo / nginx
- integration with email and Notes.app
- daily backups

Test/develop with `./main.py`  

Deploy behind nginx with `./launch.sh`

Backup, fetch email, and transfer from Notes with `crontab`



### install

    brew install mongodb  
    brew install uwsgi  
    sudo pip3 install flask  
    sudo pip3 install uwsgi  
    sudo pip3 install pymongo  
    sudo pip3 install diff-match-patch  
    sudo pip3 install requests  
    sudo pip3 install pillow  
    sudo pip3 install PyYAML  
    sudo pip3 install python-geohash  
    sudo pip3 install dateutil  
    sudo pip3 install pytz  
    sudo pip3 install boto3

### server

    /usr/local/etc/nginx/nginx.conf  
    /usr/local/etc/mongod.conf  

    brew services restart nginx  
    brew services restart mongodb  


### ref

    https://gist.github.com/mplewis/6076082
