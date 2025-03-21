import json
import boto3 # Importando a biblioteca boto3 para trabalhar com os serviços da AWS
import os # Para recuperar variáveis de ambiente

dynamydb_resource = boto3.resource('dynamodb')

table_name = os.environ['TABLE_NAME'] # Nome da tabela do DynamoDB
table = dynamydb_resource.Table(table_name)

def lambda_handler(event, context):
    response = table.scan()
    data = response.get('Items', [])
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }
    