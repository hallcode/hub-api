from flask import current_app as app

import boto3, os
from botocore.exceptions import ClientError


def get_email_template(name):
    path = app.config['TEMPLATE_PATH']
    path = os.path.join(path, 'email', name)

    with open(path, 'r') as file:
        return file.read()


def send_email(recipient, subject, body_html, body_text, sender_name=None):
    AWS_REGION = "eu-west-1"
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    if sender_name is None:
        sender_name = 'Peterborough Tenants\'s Union'

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
            Source='{:s} <{:s}>'.format(sender_name, app.config['GLOBAL_FROM_ADDR']),
        )
    except ClientError as e:
        return False
    else:
        return response
