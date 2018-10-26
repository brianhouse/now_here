#!/usr/local/bin/python3

import boto3

s3 = boto3.resource('s3')

# for bucket in s3.buckets.all():
#     print(bucket.name)

data = open("/Users/house/now_here/backup.tar.gz", 'rb')
s3.Bucket('now-here-backup').put_object(Key="backup.tar.gz", Body=data)
