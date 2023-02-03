
import boto3
import datetime
import json

s3 = boto3.resource('s3')

def create_key():
    """
    """
    replace_strs = [" ", ":", "."]

    dt = str(datetime.datetime.now())
    for replace_str in replace_strs:
        dt = dt.replace(replace_str, "-")

    return f'{dt}.json'


def put_object(data, bucket, key=None):
    """
    """
    if key is None:
        key = create_key()
    
    s3_obj = s3.Object(bucket, key)
    s3_obj.put(Body=json.dumps(data))
    print(f"Object stored at: s3://{bucket}/{key}")

    return {
        "bucket": bucket, 
        "key": key,
    }
