import json
import boto3 # Importando a biblioteca boto3 para trabalhar com os serviços da AWS
import os # Para recuperar variáveis de ambiente

dynamydb_resource = boto3.resource('dynamodb')

table_name = os.environ['TABLE_NAME'] # Nome da tabela do DynamoDB
table = dynamydb_resource.Table(table_name)

def lambda_handler(event, context):

    item_id = event.get('queryStringParameters', {}).get('id')

    if item_id:
        response = table.get_item(Key={'id': item_id})
        item = response.get('Item', {})
        
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(item)
    }
    