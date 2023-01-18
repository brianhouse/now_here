#!/Users/house/Studio/now_here/venv/bin/python

import boto3, datetime

s3 = boto3.resource('s3')

# for bucket in s3.buckets.all():
#     print(bucket.name)
d = datetime.datetime.now().strftime("%d")


data = open("/Users/house/Studio/now_here/nh.tar.gz", 'rb')
try:
    s3.Bucket('brian-house-archive').put_object(Key=f"nh/nh_{d}.tar.gz", Body=data)
except Exception as e:
    print("Upload failed: %s" % e)
