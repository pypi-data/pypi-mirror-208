
from abc import ABC, abstractmethod
from typing import List
from platinumtools.aws_classes.class_helpers import *
import boto3


class JobScheduler(ABC):
    """Publishes the data to SQS, also
        can publishes to the raw database
        the information to be processed
        later on by the commonprocessor.
    """

    def __init__(self, rawPublishinStrategies: List[DatabaseProvider]):
        self.rawPublishingStrategies = rawPublishinStrategies
    
    def publishRaw(self, events: List[dict]):
        for publishingStrategy in self.rawPublishingStrategies:
            publishingStrategy.publish(events)  
    
    @abstractmethod
    def scheduleJob(self, events: List[dict]):
        print("Scheduling Job from event: ", events)
        pass

class SingleSQSJobScheduler(JobScheduler):
    """Single job scheduler only created to be publishing into a single queue
    """
    def __init__(self, rawPublishinStrategies: List[DatabaseProvider], sqs_enpoint: str = "https://sqs.us-east-1.amazonaws.com/796522278827/MockQueue.fifo"):
        super().__init__(rawPublishinStrategies)
        self.sqs_enpoint  = sqs_enpoint
        self.client = boto3.client("sqs")

    def scheduleJob(self, events: List[dict]):
        super().scheduleJob(events) # for debugging
        for event in events:
            job = {"guid": event["guid"], "type": event["type"]}

            job_as_str = json.dumps(job)
            message_group_id = Utils.createRandomStr()
            

            response = self.client.send_message(
                MessageDeduplicationId = message_group_id,
                MessageGroupId=message_group_id,
                QueueUrl = self.sqs_enpoint, 
                MessageBody = job_as_str)





