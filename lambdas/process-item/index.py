import boto3
import os
import json

sqs_client = boto3.client("sqs")
dynamo_client = boto3.client('dynamodb')
event_client = boto3.client('events')

def handler(event, context):
    for record in event['Records']:
        body = json.loads(record["body"])
        entry = {
            "item": body["item"],
            "channel": body["channel"]
        }
        put_events_response = event_client.put_events(
            Entries=[
                {
                    "Source": body["source"],
                    "Detail": json.dumps(entry),
                    "EventBusName": os.environ["EVENT_BUS_NAME"],
                    "DetailType": "New RSS Item"
                }
            ]
        )
        print(put_events_response)
        dynamo_client.put_item(
            TableName=os.environ["DYNAMO_TABLE"],
            Item={
                "source": {
                    "S": body["source"]
                },
                "guid": {
                    "S": body["item"]["guid"]
                }
            }
        )
        sqs_client.delete_message(
            QueueUrl=os.environ["ITEM_QUEUE_URL"],
            ReceiptHandle=record["receiptHandle"]
        )