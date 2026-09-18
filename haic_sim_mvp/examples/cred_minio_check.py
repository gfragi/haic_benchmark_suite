import boto3

sts = boto3.client("sts")
print(sts.get_caller_identity())

s3 = boto3.client("s3")
try:
    s3.head_bucket(Bucket="smart-finance-results")
except Exception as e:
    print(e)