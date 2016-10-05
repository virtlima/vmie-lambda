import boto3

# Function to Disable Even to Trigger Check Status Lambda Function
def disable_check():
	events.disable_rule(
		Name = 'vmie_check_status'
		)
	print "Status Check Disabled"

# Function  to Update Status of Each Import Task
def update_status():
	diff = list(set(ddb_task_list) - set(active_task_list))
	
	if diff:
		current_stat = ec2.describe_import_image_tasks(ImportTaskIds = diff)

		for task in current_stat[u'ImportImageTasks']:
			if task[u'Status'] == 'completed':
				status_table.update_item(
					Key = {'ImportTaskId': task[u'ImportTaskId']
					},
					UpdateExpression="set JobStatus=:js, StatusMessage=:sm",
					ExpressionAttributeValues={
						':js': task[u'Status'],
						':sm': 'Completed Successfully'
					},
					ReturnValues="UPDATED_NEW"
				)

			elif task[u'Status'] in ('deleted', 'deleting'):
				status_table.update_item(
					Key = {'ImportTaskId': task[u'ImportTaskId']
					},
					UpdateExpression="set JobStatus=:js, StatusMessage=:sm",
					ExpressionAttributeValues={
						':js': task[u'Status'],
						':sm': task[u'StatusMessage']
						},
					ReturnValues="UPDATED_NEW"
				)
			else:
				print 'Nothing Matched'

	send_notification()

# Function to Send Notification on Updates and deletes Key from DDB Table. 
def send_notification():
	for items in ddb_tasks[u'Items']:
		if items[u'JobStatus'] in ('completed', 'deleted', 'deleting'):
			sns.publish(
				TopicArn='arn:aws:sns:{}:{}:vmie_status'.format(items[u'AWSRegion'], items[u'AccountId']),
				Message='''VM import task with Task ID of {} has ended with status of:\n {} \n 
				This task was importing the following object:\n {}.'''.format(items[u'ImportTaskId'], items[u'StatusMessage'], items[u'ObjectName']),
				Subject='{} Ended'.format(items[u'ImportTaskId']),
			)

			status_table.delete_item(
				Key = {'ImportTaskId': items[u'ImportTaskId']
				},
			)
			print "Notification Sent"
	if ddb_task_list == []:
		disable_check()

def lambda_handler(event, context):
	for items in ddb_tasks[u'Items']:
		ddb_task_list.append(items[u'ImportTaskId'])

		active_tasks = ec2.describe_import_image_tasks(
			Filters=[
				{
			'Name': 'task-state',
			'Values': ['active',]
				},
			]
		)

		for task_id in active_tasks[u'ImportImageTasks']:
			active_task_list.append(task_id[u'ImportTaskId'])
	
	update_status()

# Globally Defined Items
ec2 = boto3.client('ec2')
ddb = boto3.resource('dynamodb')
sns = boto3.client('sns')
events = boto3.client('events')

ddb_task_list = []
active_task_list = []

status_table = ddb.Table('vmie_status')
ddb_tasks = status_table.scan()
