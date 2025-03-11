import json
import boto3 # Importando a biblioteca boto3 para trabalhar com os serviços da AWS
import os # Para recuperar variáveis de ambiente
import uuid # Para gerar um ID único
from datetime import datetime 

bedrock_client = boto3.client("bedrock-runtime")
dynamydb_resource = boto3.resource('dynamodb')
sns_client = boto3.client("sns")

model_id = os.environ['MODEL_ID'] # ID do modelo de Machine Learning criado no Bedrock
prompt_title = os.environ['PROMPT_TITLE'] # Título do prompt criado no Bedrock
prompt_description = os.environ['PROMPT_DESCRIPTION'] # Descrição do prompt criado no Bedrock
table_name = os.environ['TABLE_NAME'] # Nome da tabela do DynamoDB
sns_topic_arn = os.environ['SNS_TOPIC_ARN'] # Amazon Resource Name do Tópico SNS


table = dynamydb_resource.Table(table_name)


def send_sms_notification(title, item_id):
    
    message = f"Conteúdo {title} gerado. ID: {item_id}"
    
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=message
    )

def save_to_dynamodb(title, content, labels):
    item_id = str(uuid.uuid4())
    createdAt = datetime.now().isoformat()

    item = {	
        'id': item_id,
        'createdAt': createdAt,
        'title': title,
        'content': content,
        'labels': labels,
        'modelId': model_id
    }

    table.put_item(Item=item)

    return item_id

def invoke_bedrock(prompt):
    # Função para invocar o modelo de Machine Learning criado no Bedrock
    request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.5,
        "messages":[
            {
                "role":"user",
                "content": [{"type":"text", "text": prompt}]
            }
        ]
    }
    
    # Carrega o request em formato JSON
    json_request = json.dumps(request)
    
    # Invoca o modelo de Machine Learning
    response = bedrock_client.invoke_model(modelId=model_id, body=json_request)
    
    # Carrega a resposta em formato JSON
    model_response = json.loads(response['body'].read())
    
    # Recupera o texto da resposta
    text_response = model_response['content'][0]['text']
    
    return text_response

def lambda_handler(event, context):
    # Capturar evento SQS
    if 'Records' in event:
        for record in event['Records']:
            message_body = json.loads(record['body'])
            print(message_body)
            
            labels = message_body.get('labels',{})
            
            prompt_title_final = f"{prompt_title}  {', '.join(labels)}"
            
            response_title = invoke_bedrock(prompt_title_final)
            
            prompt_description_final = f"{prompt_description}  {', '.join(labels)} Titulo do Produto:{response_title} "
            
            response_description = invoke_bedrock(prompt_description_final)
            
            print(response_title)
            print(response_description)
            
            item_id = save_to_dynamodb(response_title, response_description, labels)

            send_sms_notification(response_title, item_id)
    