# AWS_Lambda
Couple of AWS_Lambda functions I wrote.


1. Lambda_S3_SES.py
This function is triggered by PUT objects in S3. 
The function downloads the added object and sends it as an attachment to a specified recipient using Amazon SES (Simple Email Service).
  You need to create the bucket in S3.
  Create your function then add the bucket as trigger (PUT is the method used).

