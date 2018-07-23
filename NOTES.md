### todo
images

### install

brew install uwsgi
brew install mongodb
pip3 install flask
pip3 install uwsgi
pip3 install pymongo
pip3 install diff-match-patch


### porting notes
- python3
- run via flash + nginx
- mongo
- if term is in quotes, it does full text search, otherwise tag search only (if no tags found, cascade to full text)
- get rid of ajax style loading, have a path scheme
- make a cron that auto backsup
- make a cron that auto pulls from Notes and puts into nowhere when Note is older than a week

Applescript is slow as shit
2739 / 1.5s
~30 minutes to run once
  

//

wow, fuck. there are multiple tables in there. did everything get migrated at some point? and was it successful?

I already dont like how complicated it is to have nginx + uwsgi + flask, but ok. only difference is you launch a different daemon to keep it up rather than the app itself which is for development


///


### server

/usr/local/etc/nginx/nginx.conf 
/usr/local/etc/mongod.conf

brew services restart nginx
brew services restart mongodb


### detritus

var tags = $('#search').attr('placeholder', 'tags..');
onFocus="$('#search').val('');
