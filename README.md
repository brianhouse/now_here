# Now/Here  

Simple browser-based note-taking.
- tagging
- full-text search
- location aware
- links
- stores diffs
- uses Flask / Mongo / nginx
- integration with email and Notes.app
- daily backups

Test/develop with `./main.py`  

Deploy with `./launch.sh`

Backup, fetch email, and transfer from Notes with `crontab`



### install

    brew install mongodb  
    brew install uwsgi  
    sudo pip install flask  
    sudo pip install uwsgi  
    sudo pip install pymongo  
    sudo pip install diff-match-patch  
    sudo pip install requests  
    sudo pip install pillow  
    sudo pip install PyYAML  
    sudo pip install python-geohash  
    sudo pip install python-dateutil  
    sudo pip install pytz  
    sudo pip install boto3

### server

    /usr/local/etc/mongod.conf  

    brew services restart mongodb  


### ref

    https://gist.github.com/mplewis/6076082
