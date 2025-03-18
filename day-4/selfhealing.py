import boto3
import botocore.config
import json
import requests

from datetime import datetime

# Slack webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_to_slack(message):
    """Send a message to Slack"""
    response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    response.raise_for_status()


def blog_generate_using_bedrock():
    prompt=f"""Debug steps to rectify cpu utilization alert triggered by prometheus for my application deployed in EKS"""

    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3}))
        response=bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-70b-instruct-v1:0")

        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog:{e}")
        return ""



def lambda_handler(event, context):
    # TODO implement
    #event=json.loads(event['body'])
    #blogtopic=event['blog_topic']

    generate_blog=blog_generate_using_bedrock()

    if generate_blog:
        send_to_slack(generate_blog)


    else:
        print("No response from AI model")

    return{
        'statusCode':200,
        'body':json.dumps('Blog Generation is completed')
    }
