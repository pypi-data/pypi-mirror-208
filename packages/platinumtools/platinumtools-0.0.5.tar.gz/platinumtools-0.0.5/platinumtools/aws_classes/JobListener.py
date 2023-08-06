import boto3
from platinumtools.aws_classes.class_enhancement import *
from platinumtools.dda_constants import *


sqs = boto3.client('sqs')
# Configure the AWS credentials and region
# aws_access_key_id = 'YOUR_ACCESS_KEY'
# aws_secret_access_key = 'YOUR_SECRET_ACCESS_KEY'
# aws_region = 'us-east-1'

# # Create an SQS client
# sqs = boto3.client('sqs', region_name=aws_region,
#                     aws_access_key_id=aws_access_key_id,
#                     aws_secret_access_key=aws_secret_access_key)


# Define the URL of your SQS queue
queue_url = 'https://sqs.us-east-1.amazonaws.com/796522278827/MockQueue.fifo'



def processFromJobParameter(job_parameters):
    
    organizationDBProvider = MockOrganizationQuerier
    publishingDBProvider = MockDatabaseProvider(credentials={}, settings={})
    processor = BetterCommonProcessor(
        job_parameters=job_parameters,
        organization_provider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider
    ) # Should expect for transformation Strategies to be automatically updated
    
    processor.runJobs() # Should also post at the Mock Database


# Receive and process SQS messages
def process_messages():
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,  # Maximum number of messages to retrieve
            WaitTimeSeconds=5  # Wait time for new messages in the queue
        )
        
        if 'Messages' in response:
            for message in response['Messages']:
                # And here you should start calling it => Making sure that the received message is a valid job => Having the received message as a dict.
                # Then what you want to to do is that once you receive the message, then you want to have the max number of messages here.

                job_parameter =  {"guid": message['Body'] }
                processFromJobParameter(job_parameter)

                # Delete then the message from the queue.     
                # Delete the message from the queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
        else:
            print('No messages in the queue.')

# Call the function to start processing messages
process_messages()
