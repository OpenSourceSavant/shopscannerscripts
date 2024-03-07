import os
import boto3
import pandas as pd
import json


##----------------SQS Config ---------------##
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAXSVH2JDIF73BUMLQ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
sqs = boto3.client('sqs', region_name='ap-southeast-2')
queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/521116731600/SwiftDeals.fifo'



def send_message_to_queue(type,json_data):

    final_json = {
        "type": type,
        "msg_data": json_data
    }

    # Convert the final JSON object to a string
    final_json_string = json.dumps(final_json)

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody= final_json_string,
        MessageGroupId='SwiftDeals'
    )

    # Check if HTTPStatusCode is 200
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Successfully added deal to Queue")
        #update_csv_count('metadata.csv')
    else:
        print("Failed adding to queue")




