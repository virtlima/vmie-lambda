import boto3

def lambda_handler(event, context):
	# Creation of Service Client Connections
	ec2 = boto3.client('ec2')
	ddb = boto3.client('dynamodb')
	sns = boto3.client('sns')
	events = boto3.client('events')
	sts = boto3.client('sts')

	#Grabbing Account ID and Region
	account_id = sts.get_caller_identity()["Account"]
	region = event[u'Records'][0][u'awsRegion']

	# Grabbing S3 Bucket and S3 Object Key from S3 Event Object
	s3_object = event[u'Records'][0][u's3'][u'object'][u'key']
	s3_bucket = event[u'Records'][0][u's3'][u'bucket'][u'name']

	# Enabling CloudWatch Event rule for Status Check
	#enable_trigger = events.put_targets(
	#	Rule = 'vmie_check_status',
	#	Targets = )
	#print 'Enabled Event'

	# Running Import Command against object from S3 Trigger
	import_vmdk = ec2.import_image(
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
	
	# Grabbing Import Task ID info to Send Notification and post to DDB
	task_id = import_vmdk[u'ImportTaskId']
	status = import_vmdk[u'Status']
	status_message = import_vmdk[u'StatusMessage']
    
	# Publishing Intiated Task Notification to SNS Topic
	message = sns.publish(
		TopicArn='arn:aws:sns:{}:{}:vmie_start'.format(region, account_id),
		Message='''A VM import task with the Task ID of {} has been started in your Account.\n 
This task is importing the following VM: {}.\n When the job has ended you will be notified of status.'''.format(task_id, s3_object),
		Subject=task_id,
		)
	print 'Notification has been sent for {}.'.format(task_id)

	# Post Status to DDB Table for tracking purposes
	post_status = ddb.put_item(
		TableName = 'vmie_status',
		Item = {
			'ImportTaskId':{'S':task_id},
			'JobStatus':{'S':status},
			'StatusMessage':{'S':status_message},
			'ObjectName':{'S':s3_object},
			}
		)
	print 'DynamoDB Entry has been created to track {}.'.format(task_id)
