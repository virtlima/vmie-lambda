# vmie-lambda
This is a AWS Lambda function that works off of a S3 Create Object Event that will import a OVA file to an AMI. This is a simple Lambda function that will take the ova file and import it to a AMI using the VM Import\Export Service. The accompanying script will continually check that status of the import jobs until they have finished and report back status.
