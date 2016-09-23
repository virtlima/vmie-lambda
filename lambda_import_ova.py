import boto3

def lambda_handler(event, context):
	ec2_client = boto3.client('ec2')
	s3_object = event[u'Records'][0][u's3'][u'object'][u'key']
	s3_bucket = event[u'Records'][0][u's3'][u'bucket'][u'name']

	import_vmdk = ec2_client.import_image(
		Description='Lambda_VMIE',
		DiskContainers=[
			{
				'Description':'Import_OVA',
				'Format':'ova',
				'UserBucket':
					{
						'S3Bucket': s3_bucket,
						'S3Key': s3_object 
					},
				},
			],
		LicenseType='BYOL'
	)
	
	import_vmdk

	return;
