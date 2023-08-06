import base64
import json

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')  # Create an S3 client

bucket_name = 'trial-report'  # specify the S3 bucket you want to download from


# Download the file
def download_from_s3(file_name, local_file_name):
    s3.download_file(bucket_name, file_name, local_file_name)  # 3rd argument is the local file name


# Re-upload the file to the same s3 bucket
def upload_to_s3(local_file_name, foreign_file_name):
    s3.upload_file(local_file_name, bucket_name, foreign_file_name)  # local file name, bucket, foreign name


def get_secret(keyname: str) -> dict or bytes:
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-2"
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=keyname
        )
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return base64.b64decode(get_secret_value_response['SecretBinary'])
    except ClientError as e:
        raise e