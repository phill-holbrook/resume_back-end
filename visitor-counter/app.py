import json
import os
import boto3


def lambda_handler(event, context):

    # Get environment variables
    table_name = os.environ["TABLE"]
    region = os.environ["REGION"]
    aws_environment = os.environ["AWSENV"]

    # Check if executing locally or on AWS, and configure DynamoDB connection accordingly.
    if aws_environment == "AWS_SAM_LOCAL":
        # Local connection string
        table = boto3.resource(
            "dynamodb",
            endpoint_url="http://host.docker.internal:8000/",
            region_name=region,
            aws_access_key_id="abcd",
            aws_secret_access_key="abcd",
        ).Table(table_name)

    else:
        # AWS
        table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    # Check if table is empty. If it is, initialize ID
    if "Item" not in table.get_item(Key={"Id": 1}).keys():
        table.put_item(Item={"Id": 1})

    # Update the visitor counter in the table
    table.update_item(
        Key={"Id": 1},
        UpdateExpression="ADD visitors :i",
        ExpressionAttributeValues={":i": 1},
    )

    # Get the current visitor counter from DynamoDB
    counter = table.get_item(Key={"Id": 1})["Item"]["visitors"]

    # Return the counter number to the API call

    response = {
        "statusCode": 200,
        "body": json.dumps({"counter": str(counter)}),
    }

    response["headers"] = {
        "Access-Control-Allow-Origin": "https://resume.hollowresearch.com"
    }

    return response
