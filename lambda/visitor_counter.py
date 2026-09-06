import boto3
import json
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        response = table.update_item(
            Key={'id': 'visitor_count'},
            UpdateExpression='SET #c = if_not_exists(#c, :zero) + :incr',
            ExpressionAttributeNames={'#c': 'count'},
            ExpressionAttributeValues={':zero': 0, ':incr': 1},
            ReturnValues='UPDATED_NEW'
        )
        new_count = int(response['Attributes']['count'])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # public read-only endpoint, safe to allow any origin
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'count': new_count})
        }

    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            'statusCode': 503,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Counter temporarily unavailable, please try again.'})
        }