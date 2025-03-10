import json
import boto3
import os
import uuid

s3_client = boto3.client('s3')


def lambda_handler(event, context):

    query_params = event.get("queryStringParameters", {})
    file_name = query_params.get("fileName")
    content_type = query_params.get("contentType")
    expiration_time = 3600

    bucket_name = os.environ.get("BUCKET_NAME")
    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket_name,
            "Key": file_name,
            "ContentType": content_type
        },
        ExpiresIn=expiration_time
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Url pré assinada criada com sucesso",
            "url": presigned_url,
            "expiration_time": expiration_time,
            "file_name": file_name,
            "content_type": content_type
        }),
    }
