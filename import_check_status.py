import boto3
import sets

# Globally Defined Items
ec2 = boto3.client('ec2')
ddb = boto3.resource('dynamodb')
sns = boto3.client('sns')
test = 'My Test String'

# Function to Disable Even to Trigger Check Status Lambda Function
def disable_check():
	events = boto3.client('events')
	disable_event = events.disable_rule(
		Name = 'vmie_check_status'
		)
	describe_event = events.describe_rule(
		Name = 'vmie_check_status')
	print describe_event

# Function  to Update Status of Each Import Task
def update_status():
	ddb_task_list = []

	status_table = ddb.Table('vmie_status')
	ddb_tasks = status_table.scan()
	
	for items in ddb_tasks[u'Items']:
		ddb_task_list.append(items[u'ImportTaskId'].decode('unicode_escape').encode('ascii','ignore'))

	s1 = sets.Set(active_task_list)
	s2 = sets.Set(ddb_task_list)
	diff = list(s2-s1)
	
	if diff != []:
		current_stat = ec2.describe_import_image_tasks(ImportTaskIds = diff)

		print current_stat

		# Need to Create Code that Grabs new Status and Status Message and updates Dynamo, then triggers Notification Function

# Function to Send Notification on Updates and deletes Key from DDB Table. 
def send_notification():

	message = sns.publish(
	TopicArn='arn:aws:sns:%s:%s:vmie_status' % (region, account_id),
	Message='VM import task with Task ID of %s has ended with status of:\n %s \n This import task was for %s.' % ('ImportTaskId', 'StatusMessage', 'ObjectName'),
	Subject='%s Ended' % (task_id),
	)

# Code Starts Here
active_tasks = ec2.describe_import_image_tasks(
    Filters=[
        {
            'Name': 'task-state',
            'Values': [
                'completed',
            ]
        },
    ]
)

active_task_list = []

for task_id in active_tasks[u'ImportImageTasks']:
	active_task_list.append(task_id[u'ImportTaskId'])

# Need to add If Statement on DynamoDB Trigger on Update to Table. 

if active_task_list == []:
	disable_check()

else: update_status()

