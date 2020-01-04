DIR=/Users/house/Studio/now_here/backup
/usr/local/bin/mongodump -d nh -o $DIR > /dev/null 2>&1
tar -zcf $DIR.tar.gz $DIR > /dev/null 2>&1
rm -r $DIR
/Users/house/Studio/now_here/upload.py
# idea here being that an updated backup is available to Time Machine
