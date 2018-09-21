DIR=/Users/house/Projects/now_here/backup
/usr/local/bin/mongodump -d nh -o $DIR > /dev/null 2>&1
tar -zcf $DIR.tar.gz $DIR > /dev/null 2>&1
rm -r $DIR
# sshpass -p PASSWORD scp -r $DIR.tar.gz house3012@brianhouse.net:backup


# idea here being that an updated backup is available to Time Machine
