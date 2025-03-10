import json
import boto3
import os

rekognition_client = boto3.client('rekognition')
sqs_client = boto3.client('sqs')

def lambda_handler(event, context):

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']

    print(event)
    print(bucket_name)
    print(file_name)

    response = rekognition_client.detect_labels(
        Image={'S3Object': {'Bucket':bucket_name, 'Name': file_name }},
        MaxLabels=10,
        MinConfidence=80
    )

    labels = [label['Name'] for label in response['Labels']]

    print(labels)

    sqs_client.send_message(
        QueueUrl=os.environ['SQS_URL'],
        MessageBody=json.dumps({
            'bucket': bucket_name,
            'key': file_name,
            'labels': labels
        })
    )
