DIR=/Users/house/Studio/now_here/
/usr/local/bin/mongodump -d nh -o $DIR > /dev/null 2>&1
tar -zcf $DIR/nh.tar.gz nh -C $DIR nh > /dev/null 2>&1
rm -r $DIR/nh
/Users/house/Studio/now_here/upload.py
# idea here being that an updated backup is available to Time Machine
