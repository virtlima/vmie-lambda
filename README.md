# vmie-lambda
This is a set of AWS Lambda Functions and CloudFormation Template to make it easier to utilize the AWS VM Import\Export Service to import OVA files into AMIs. Below is a description of each component and how to deploy it within your AWS account. 

### vmie-solution.yaml
This is a Cloudformation Template that deploys the Lambda functions and supporting infrastructure to monitor the tasks. This template also sets up all the needed permissions for the VM Import service to work within your AWS account. You need to deploy this template first. Upload the Zip files to a S3 Bucket within your account, then make sure to update the Lambda function sections (ImportOva and CheckImport Sections) with that S3 bucket. 

### vmie-s3-bucket-update.yaml
After you have deployed the first template, you will then need to deploy this template to updated the S3 Bucket with the lambda function trigger. Make sure to update the Lambda function sections (ImportOva and CheckImport Sections) with that S3 bucket. 

### import_ova.zip and import_ova.py
The import_ova.py is in the zip file. Copy the import_ova.zip file to a S3 bucket and make sure to update the cfn template with that bucket to deploy the lambda function. The import_ova function will trigger when a file with an .ova extension is placed into the S3 bucket created by the cfn template. This will also create an entry in a DynamoDB table to track the import task, and enable the check import status function to check the task every 30 minutes and send a notification that the import task has begun.  

### check_import_status.zip and check_import_status.py
The check_import_status.py is in the zip file. Copy the check_import_status.zip file to a S3 bucket and make sure to update the cfn template with that bucket to deploy the lambda function. The check_import_status function when enabled will check the status of the import task every 30 Minutes. When the task is completed or failed it will send a notification. 
