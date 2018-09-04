DIR=/Users/house/Projects/now_here/backup
/usr/local/bin/mongodump -d nh -o $DIR > /dev/null
tar -zcvf $DIR.tar.gz $DIR
rm -r $DIR

# idea here being that an updated backup is available to Time Machine
