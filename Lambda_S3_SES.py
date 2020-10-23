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
email_sender = 'sender_email_here'
email_recipient = 'recipient_email_here'
email_subject = 'New Object Added to testjakor bucket in S3'
email_body = 'Hello, The Attached file was just added to your S3 bucket'
# The HTML body of the email.
email_body_html = """\
    <html>
    <head></head>
    <body>
    <h1>Hello!</h1>
    <p>The Attached file was just added to your S3 bucket.</p>
    </body>
    </html>
    """

def lambda_handler(event, context):
    # Create an S3 and SES client
    s3 = boto3.client('s3')
    ses = boto3.client('ses', region_name='us-east-1')

    # Bucket Name where file was uploaded
    source_bucket = event["Records"][0]['s3']['bucket']['name']
    # Extract object info and path and store it as a variable
    key = event['Records'][0]['s3']['object']['key']
    file_pathname = key.replace("+", " ")
    #temporary store the file in tmp directory in lambda
    temp_file_name = '/tmp/' + os.path.basename(file_pathname)

    # Download the file from the event (extracted above) to the tmp location
    s3.download_file(source_bucket, file_pathname, temp_file_name)

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = email_subject
    msg['From'] = email_sender
    msg['To'] = email_recipient

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(email_body.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(email_body_html.encode(CHARSET), 'html', CHARSET)

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Define the attachment part and encode it using MIMEApplication.
    attachment = MIMEApplication(open(temp_file_name, 'rb').read())

    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.
    attachment.add_header('Content-Disposition', 'attachment',
                          filename=os.path.basename(temp_file_name))

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Add the attachment to the parent container.
    msg.attach(attachment)
    print(msg)
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
