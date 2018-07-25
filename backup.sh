DIR=/Users/house/Projects/now_here/backup
mongodump -d nh -o $DIR
tar -zcvf $DIR.tar.gz $DIR
rm -r $DIR

# idea here being that an updated backup is available to Time Machine
