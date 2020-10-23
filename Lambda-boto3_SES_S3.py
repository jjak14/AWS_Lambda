import os
import json
import os.path
import boto3
import email
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#initialize components of the email to be sent
email_sender = 'sender@email.com'
email_recipient = 'recipient@email.com'
email_subject = 'New Object Added to testjakor bucket in S3'
email_body = 'Hello, The Attached file was just added to your S3 bucket'


def lambda_handler(event, context):

    # Create an S3 and SES client
    s3 = boto3.client('s3')  # changed here from s3 = boto3.client('s3')
    ses = boto3.client('ses', region_name='us-east-1')

    # Extract bucket name from Event records
    bucket_name = event["Records"][0]['s3']['bucket']['name']

    # Extract object info from event records
    key = event["Records"][0]['s3']['object']['key']
    object_key = key.replace("+", " ")
    
    #temporary store the file in tmp directory in lambda
    temp_path = '/tmp/' + os.path.basename(object_key)
    s3.download_file(bucket_name, object_key, temp_path)

    # Create a multipart parent container.
    msg = MIMEMultipart()
    # build "subject", "from" and "to" parts of the message.
    msg['Subject'] = email_subject
    msg['From'] = email_sender
    msg['To'] = email_recipient

    #Building the body part of the message.
    msg_part = MIMEText(email_body, 'html', 'utf-8')

    # Add the text part to the child container.
    msg.attach(msg_part)

    # Define the attachment part and encode it using MIMEApplication.
    # Then add a header to tell the email client to treat this part as an attachment,
    attachment = MIMEApplication(open(temp_path, 'rb').read())
    attachment.add_header('Content-Disposition', 'attachment',
                          filename=os.path.basename(temp_path))

    # Add the attachment to the parent container.
    msg.attach(attachment)

    print("Message is: ", msg)

    #Send the email
    try:
        #Provide the contents of the email.
        response = ses.send_raw_email(
            Source=msg['From'],
            Destinations=[
                msg['To']
            ],
            RawMessage={
                'Data': msg.as_string(),
            }
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
