from flask import current_app as app

import boto3
from botocore.exceptions import ClientError


def send_email(recipient, subject, body_html, body_text):
    AWS_REGION = "eu-west-1"
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=app.config['GLOBAL_FROM_ADDR'],
        )
    except ClientError as e:
        return False
    else:
        return response
