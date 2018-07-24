### todo
migration: re-migrate with images?
auto-backup
Notes.app pull (when note is older than a week)
tool to normalize tags (what, is it 2004?)

Applescript is slow as shit
2739 / 1.5s
~30 minutes to run once


### install

brew install uwsgi
brew install mongodb
python3 ./setup.py --requires  

### porting notes
wow, fuck. there are multiple tables in there. did everything get migrated at some point? and was it successful?

### server

/usr/local/etc/nginx/nginx.conf 
/usr/local/etc/mongod.conf

brew services restart nginx
brew services restart mongodb


### detritus

var tags = $('#search').attr('placeholder', 'tags..');
onFocus="$('#search').val('');
