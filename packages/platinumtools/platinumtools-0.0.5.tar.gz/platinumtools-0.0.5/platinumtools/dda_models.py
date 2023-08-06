from datetime import datetime
from typing import Dict
from datetime import datetime
import uuid

class Source(str):
    pass

class Attachment:
    def __init__(self, id_attachment: str = "", uri: str = "", file_type = "", file_extension:str = "", size: int = 0):
        self.id = id_attachment
        self.uri = uri
        self.file_type = file_type
        self.file_extension = file_extension
        self.size = size

    def to_dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "file_type": self.file_type,
            "file_extension": self.file_extension,
            "size": self.size
        }


class GenericEvent:
    """Generic event inside the staging area
    """
    def __init__(self, event_guid: str, employee_guid: str, timestamp: datetime, loadbatch_id: int, raw_data: str, application: str):
        self.event_guid = event_guid
        self.employee_guid = employee_guid
        self.timestamp = timestamp
        self.loadbatch_id = loadbatch_id
        self.raw_data = raw_data
        self.application = application

    def to_dict(self):
        return {
            "event_guid": self.event_guid,
            "employee_guid": self.employee_guid,
            "timestamp": self.timestamp,
            "loadbatch_id": self.loadbatch_id,
            "raw_data": self.raw_data,
            "application": self.application
        }

class FileEvent(GenericEvent):
    def __init__(self, event_guid: str, employee_guid: str,  timestamp: datetime, loadbatch_id: int, raw_data: str, operation: str, version_source_uri: Attachment, source_uri: Attachment, application: str):
        super().__init__(event_guid, employee_guid,  timestamp, loadbatch_id, raw_data, application=application)
        self.operation = operation
        self.version_source_uri = version_source_uri
        self.source_uri = source_uri

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "operation": self.operation,
            "version_source_uri": self.version_source_uri.to_dict(),
            "source_uri": self.source_uri.to_dict(),
        })
        return event_dict

class SalesEvent(GenericEvent):
    """Version 2.0 Introduction with support for sales events
    2023-05-12 17:53:20: Where are the 
    """
    def __init__(self, event_guid: str, employee_guid: str,  timestamp: datetime, loadbatch_id: int, raw_data: str, operation: str, category: str, application: str, description: str):
        super().__init__(event_guid, employee_guid,  timestamp, loadbatch_id, raw_data, application=application)
        self.operation = operation #activity__c
        self.category = category # Object being dealed: Opportunity, Lead, Account, Contact, etc.
        self.description = description # Description of the activity

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "operation": self.operation,
            "category": self.category,
            "description": self.description
        })
        return event_dict

class ChromeEvent(SalesEvent):
    """Verion 3.0 Introduction with support for Chrome events This would be the mapped end interface.

        start_time	str
        end_time	str
        duration	double
        title	str
        description	str
        url	
        attachments	<ST-Attachment>List({id, url, file_type, file_extension_size})
        action_origin	str
        span_guid	String
        root_reference	STRING
        root_start	Datetime
        root_end	Datetime
        root_duration	Number


    """

    def __init__(self, event_guid: str, employee_guid: str, timestamp: datetime, loadbatch_id: int, raw_data: str, operation: str, category: str, application: str, description: str, 
                 start_time: str, end_time: str, duration: float, 
                 title: str, url: str, attachments: Dict[str, Attachment], 
                 action_origin: str, span_guid: str, root_reference: str, root_start: datetime, root_end: datetime, root_duration: float):
        super().__init__(event_guid, employee_guid, timestamp, loadbatch_id, raw_data, operation, category, application, description)
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.title = title
        self.url = url
        self.attachments = attachments
        self.action_origin = action_origin
        self.span_guid = span_guid
        self.root_reference = root_reference
        self.root_start = root_start
        self.root_end = root_end
        self.root_duration = root_duration




    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "title": self.title,
            "url": self.url,
            "attachments": self.attachments,
            "action_origin": self.action_origin,
            "span_guid": self.span_guid,
            "root_reference": self.root_reference,
            "root_start": self.root_start,
            "root_end": self.root_end,
            "root_duration": self.root_duration
        })
        return event_dict
        

class StagingModel():
    def __init__(self, version = "", connector_guid="", type = "", organization_guid = "", actor = "", item_count = 2, details = [], hash_1 = "", hash_2 = ""):
        self.guid = str(uuid.uuid4()) #Random GUID
        self.version = version
        self.connector_guid = connector_guid
        self.type = type
        self.organization_guid = organization_guid
        self.actor = actor
        self.item_count = item_count
        self.details = details
        self.hash_1 = hash_1
        self.hash_2 = hash_2

    def to_dict(self):
        return {
            "guid": self.guid,
            "version": self.version,
            "connector_guid": self.connector_guid,
            "type": self.type,
            "organization_guid": self.organization_guid,
            "actor": self.actor,
            "item_count": self.item_count,
            "details": self.details,
            "hash_1": self.hash_1,
            "hash_2": self.hash_2
        }
    
    def hash_model(self):
        """Using the content (details) it hashes into an secure key
        """
        return ""

    def test_hash(self, key):
        """Pass the key in order to unhash and test if the content hadn't een modified

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        return True
    
    
    def populate_properties_from_dict(self, data: dict):
        """
        Populate the instance properties from a dictionary.
        """
        if 'guid' in data:
            self.guid = data['guid']
        if 'version' in data:
            self.version = data['version']
        if 'connector_guid' in data:
            self.connector_guid = data['connector_guid']
        if 'type' in data:
            self.type = data['type']
        if 'organization_guid' in data:
            self.organization_guid = data['organization_guid']
        if 'actor' in data:
            self.actor = data['actor']
        if 'item_count' in data:
            self.item_count = data['item_count']
        if 'details' in data:
            self.details = data['details']
        if 'hash_1' in data:
            self.hash_1 = data['hash_1']
        if 'hash_2' in data:
            self.hash_2 = data['hash_2']
    

class ManagementAPIStagingModel(StagingModel):
    def __init__(self,  organization_guid="", actor="", item_count=2, details=[]):
        super().__init__("1.0", "365_MANAGEMENT", organization_guid, actor, item_count, details)




