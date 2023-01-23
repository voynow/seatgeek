import json

def lambda_handler(event, context):
    # test comment
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
