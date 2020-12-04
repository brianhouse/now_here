#!/usr/local/bin/python3

import boto3

s3 = boto3.resource('s3')

# for bucket in s3.buckets.all():
#     print(bucket.name)

data = open("/Users/house/Studio/now_here/backup.tar.gz", 'rb')
try:
    s3.Bucket('brian-house-archive').put_object(Key="now_here.tar.gz", Body=data)
except Exception as e:
    print("Upload failed: %s" % e)
