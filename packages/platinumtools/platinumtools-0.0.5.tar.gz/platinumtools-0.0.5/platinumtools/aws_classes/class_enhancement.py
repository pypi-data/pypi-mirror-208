
from abc import ABC, abstractmethod
from platinumtools.aws_classes.class_helpers import *
from platinumtools.dda_constants import *
from typing import List
from platinumtools.aws_classes.config_mapper_df import ConfigMapper
import pandas as pd
from platinumtools.dda_models import *


class SourceAdapter(ABC):
    """Transformation for Status Types Interfaces, 
    some might come in json or have different namings, the idea is to convert them
    into the standard interfaces.
    """
    @abstractmethod
    def adapt(staging_events: dict)->dict:
        pass

class StatusAdapter(SourceAdapter):
    """Transformation for Status Types Interfaces
    """

    def adapt(staging_events: dict)->dict:
        pass

class MockAdapter(SourceAdapter):
    """Mock Adaptation to be used until the other interfaces work.
    """

    # I will be mocking a standard interface with evertything one could have?
    def __init__(self) -> None:
        super().__init__()
        self.mock_adapt_result ={'guid':'a08f815f-12fa-47fb-9f6d-5c3d7fe53eff','version':'1.0','connector_guid':'365_MANAGEMENT','type':'','organization_guid':'74d25673-b01c-4211-a7c4-9930610fb7eb','actor':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','operation':2,'item_count':5,'details':[{'event_guid':'74d25673-b01c-4211-a7c4-9930610fb7eb','employee_guid':'ab3c-asd1-100G','timestamp':'2022-10-24T18:23:36','loadbatch_id':'a08f815f-12fa-47fb-9f6d-5c3d7fe53eff','raw_data':{'CreationTime':'2022-10-24T18:23:36','Id':'c878338a-15ff-4986-8bd3-5d6eac071b4a','Operation':'MipLabel','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':43,'UserKey':'c397ec65-e71e-493f-94f2-2e53cdd9b02e','UserType':4,'Version':1,'Workload':'Exchange','ObjectId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','UserId':'nelson@o365.devcooks.com','ApplicationMode':'Standard','ItemName':'HelloThere','LabelAction':'None','LabelAppliedDateTime':'2022-10-25T18:23:32','LabelId':'defa4170-0d19-0005-0004-bc88714345d2','LabelName':'AllEmployees(unrestricted)','Receivers':['nwang@platinumfilings.com','wangnelson2@gmail.com'],'Sender':'nelson@o365.devcooks.com'},'application':'Exchange','operation':'MipLabel','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'74d25673-b01c-4211-a7c4-9930610fb7eb','employee_guid':'ab3c-asd1-100G','timestamp':'2022-10-25T18:23:36','loadbatch_id':'a08f815f-12fa-47fb-9f6d-5c3d7fe53eff','raw_data':{'CreationTime':'2022-10-25T18:23:36','Id':'c17eedb7-6977-4169-b625-bb26e0ede079','Operation':'MipLabel','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':13,'UserKey':'c397ec65-e71e-493f-94f2-2e53cdd9b02e','UserType':4,'Version':1,'Workload':'Exchange','ObjectId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','UserId':'nelson@o365.devcooks.com','IncidentId':'11bb1d67-ae3d-d176-4000-08dab6b85275','PolicyDetails':[{'PolicyId':'00000000-0000-0000-0000-000000000000','Rules':[{'Actions':[],'ConditionsMatched':{'ConditionMatchedInNewScheme':True,'OtherConditions':[{'Name':'SensitivityLabels','Value':'defa4170-0d19-0005-0004-bc88714345d2'}]},'RuleId':'defa4170-0d19-0005-0004-bc88714345d2','RuleMode':'Enable','RuleName':'defa4170-0d19-0005-0004-bc88714345d2','Severity':'Low'}]}],'SensitiveInfoDetectionIsIncluded':False,'ExchangeMetaData':{'BCC':[],'CC':[],'FileSize':17579,'From':'nelson@o365.devcooks.com','MessageID':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','RecipientCount':2,'Sent':'2022-10-25T18:23:33','Subject':'HelloThere','To':['nwang@platinumfilings.com','wangnelson2@gmail.com'],'UniqueID':'fe03264d-a22d-4c70-57b1-08dab6b60675'}},'application':'Exchange','operation':'MipLabel','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'74d25673-b01c-4211-a7c4-9930610fb7eb','employee_guid':'ab3c-asd1-100G','timestamp':'2022-10-25T18:23:33','loadbatch_id':'a08f815f-12fa-47fb-9f6d-5c3d7fe53eff','raw_data':{'CreationTime':'2022-10-25T18:23:33','Id':'e01bd1fb-a635-4f09-57b1-08dab6b60675','Operation':'Send','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':2,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','ClientIP':'68.160.247.154','UserId':'nelson@o365.devcooks.com','AppId':'00000002-0000-0ff1-ce00-000000000000','ClientIPAddress':'68.160.247.154','ClientInfoString':'Client=OWA;Action=ViaProxy','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','SessionId':'e01c84f0-8db1-439e-87bc-5ee52fdf90d4','Item':{'Id':'Unknown','InternetMessageId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','ParentFolder':{'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEPAAAB','Path':'\\Drafts'},'SizeInBytes':3991,'Subject':'HelloThere'}},'application':'Exchange','operation':'Send','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'74d25673-b01c-4211-a7c4-9930610fb7eb','employee_guid':'ab3c-asd1-100G','timestamp':'2022-10-25T18:23:04','loadbatch_id':'a08f815f-12fa-47fb-9f6d-5c3d7fe53eff','raw_data':{'CreationTime':'2022-10-25T18:23:04','Id':'daf566de-6581-486c-b9f7-f8df1d07457f','Operation':'MailItemsAccessed','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':50,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','UserId':'nelson@o365.devcooks.com','AppId':'00000002-0000-0ff1-ce00-000000000000','ClientIPAddress':'68.160.247.154','ClientInfoString':'Client=OWA;Action=ViaProxy','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OperationProperties':[{'Name':'MailAccessType','Value':'Bind'},{'Name':'IsThrottled','Value':'False'}],'OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','SessionId':'e01c84f0-8db1-439e-87bc-5ee52fdf90d4','Folders':[{'FolderItems':[{'InternetMessageId':'<ceafc3fa-fd0a-46ba-9754-e033ee56ce75@az.westcentralus.production.microsoft.com>'},{'InternetMessageId':'<ae042a57-4cd4-466a-adf0-417549c30a96@az.westeurope.production.microsoft.com>'},{'InternetMessageId':'<abccdb15-1bd4-476f-88f8-0bde5349cb61@az.westus2.production.microsoft.com>'},{'InternetMessageId':'<5c06433f-d7f6-48c7-8752-72f5cf93011c@az.westus.production.microsoft.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEMAAAB','Path':'\\Inbox'},{'FolderItems':[{'InternetMessageId':'<CY5PR05MB91439309823940F866A9629EDD2E9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB9143FB7EF878879EED5FC05CDD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB91439292F10817DCB3DE6FC6DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB91436B02DD20921A28720BA4DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB','Path':'\\SentItems'}],'OperationCount':8},'application':'Exchange','operation':'MailItemsAccessed','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'74d25673-b01c-4211-a7c4-9930610fb7eb','employee_guid':'ab3c-asd1-100G','timestamp':'2022-10-25T18:23:41','loadbatch_id':'a08f815f-12fa-47fb-9f6d-5c3d7fe53eff','raw_data':{'CreationTime':'2022-10-25T18:23:41','Id':'0d77eaad-2ddd-4e39-8ce1-469113caf263','Operation':'MailItemsAccessed','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':50,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','UserId':'nelson@o365.devcooks.com','AppId':'13937bba-652e-4c46-b222-3003f4d1ff97','ClientAppId':'13937bba-652e-4c46-b222-3003f4d1ff97','ClientIPAddress':'2603:10b6:930:3d::7','ClientInfoString':'Client=REST;Client=RESTSystem;;','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OperationProperties':[{'Name':'MailAccessType','Value':'Bind'},{'Name':'IsThrottled','Value':'False'}],'OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','Folders':[{'FolderItems':[{'InternetMessageId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB','Path':'\\SentItems'}],'OperationCount':1},'application':'Exchange','operation':'MailItemsAccessed','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}}],'hash_1':'','hash_2':''}

    def adapt(self, staging_events: dict)->dict:
        return self.mock_adapt_result


class Microsoft365ManagementAdapter(SourceAdapter):

    def __init__(self, organizationQuerier: OrganizationalQuerier):
        self.organizationalQuerier = organizationQuerier

    def adapt(self, staging_events: dict) -> dict:
        """Staging event (with 
        Args:
            staging_events (dict): Converted Staging event.

        Returns:
            dict: _description_
        """
        
        management_api = ManagementAPIStagingModel()

        management_api.populate_properties_from_dict(staging_events)


        organization_params  = self.organizationalQuerier.getOrganizationParameters_365(
            orgnaization_guid_365=management_api.organization_guid
        )

        new_details = []
        for event in management_api.details:
            employee_id = event["UserId"]
            fileEvent = FileEvent(
                version_source_uri=Attachment(), #For now empty
                source_uri=Attachment(), #For now empty
                operation=event["Operation"],
                
                
                event_guid=management_api.organization_guid,
                employee_guid=organization_params[employee_id]["employee_id"],
                application=event["Workload"],
                timestamp=event["CreationTime"],
                loadbatch_id=management_api.guid,
                raw_data=event,
            )
            new_details.append(fileEvent.to_dict())

        management_api.details = new_details # Replace with updated interfaces

        return management_api.to_dict()


class ChromeAdapter(SourceAdapter):


    def __init__ (self, organizationQuerier: OrganizationalQuerier):
        self.organizationalQuerier = organizationQuerier
    
    def adapt(self, staging_events: dict) -> dict:
        """Staging event from a CHROME Application

        Args:
            staging_events (dict): _description_

        Returns:
            dict: _description_
        """
        
        management_api = ManagementAPIStagingModel()
        management_api.populate_properties_from_dict(staging_events)

        # Organization specific processes
        print("management_api.organization_guid=>", management_api.organization_guid, len(management_api.organization_guid))
        organization_params  = self.organizationalQuerier.getOrganizationParameters_clientguid(
            client_guid=management_api.organization_guid
        )


        # This have to do with building the right interface
        new_details = []
        for event in management_api.details:
            employee_id = staging_events["connector_guid"] # As there should be only one employee per client, this is the employee_id


            # def __init__(self, event_guid: str, employee_guid: str, timestamp: datetime, loadbatch_id: int, raw_data: str, operation: str, category: str, application: str, description: str, 
            #      start_time: str, end_time: str, duration: float, 
            #      title: str, url: str, attachments: Dict[str, Attachment], 
            #      action_origin: str): 
            # def __init__(self, event_guid: str, employee_guid: str,  timestamp: datetime, loadbatch_id: int, raw_data: str, operation: str, category: str, application: str, description: str):

            def eventActiveStatus(event):
                """Determines if the event ACTIVITY Status for Chrome Extension

                Args:
                    event (str): Event Active Status

                Returns:
                    str: ACTIVE | PASSOVE
                """
                interactions = event["interactions"] if "interactions" in event else {}
                # if the keys are more than 0, then it is active
                if len(interactions.keys()) > 0:
                    return "ACTIVE"
                else:
                    return "PASSIVE"

            # Receive data regarding the span guid
            span_guid = event["spanId"] if "spanId" in event else ""
            event_endtime = event["endTime"] if "endTime" in event else event["timestamp"]
            event_duration = event["duration"] if "duration" in event else 0
            
            # Receive data regarding the span guid from the Organization Querier using isRootOrUpdateRoot
            
            # In form of {is_root: bool, total_duration: number, root_reference: str}
            
            span_guid_data = self.organizationalQuerier.isRootOrUpdateRoot(span_guid=span_guid, event_endtime=event_endtime, event_duration=event_duration )
            is_root = span_guid_data["is_root"] # This is the is_root that will be used for the event
            total_duration = span_guid_data["total_duration"] # This is the root_duration that will be used for the event
            root_reference = span_guid_data["root_reference"] # This is the root_reference that will be used for the event

            # Remeber to null safe all this
            fileEvent = ChromeEvent(
                event_guid=management_api.organization_guid,
                employee_guid=organization_params[employee_id]["employee_guid"],
                timestamp=event["timestamp"], #Always
                loadbatch_id=management_api.guid,
                raw_data=event,
                category=event["domain"] if "domain" in event else "",
                operation=event["type"] if "type" in event else "",
                application=event["domain"] if "domain" in event else "",
                description=event["interactions"] if "interactions" in event else {},

                start_time=event["startTime"] if "startTime" in event else event["timestamp"],
                end_time=event["endTime"] if "endTime" in event else event["timestamp"],
                duration=event["duration"] if "duration" in event else 0,
                title=event["title"] if "title" in event else "",
                url=event["url"] if "url" in event else "",
                attachments=event["files"] if  "files" in event else {},
                action_origin=eventActiveStatus(event),
                span_guid=span_guid,
                root_reference= "IS_ROOT" if is_root else root_reference,
                root_duration=total_duration if is_root else 0,
                root_start = event["startTime"] if is_root and "startTime" in event else "",
                root_end = event["endTime"] if is_root and "endTime" in event else "",
            )

            new_details.append(fileEvent.to_dict())

        management_api.details = new_details # Replace with updated interfaces

        return management_api.to_dict()



class SalesforceAdapter(SourceAdapter):

    def __init__(self, organizationQuerier: OrganizationalQuerier):
        self.organizationalQuerier = organizationQuerier

    def adapt(self, staging_events: dict) -> dict:
        """Staging event (with 365 details into 365 adapted source.)
        Args:
            staging_events (dict): Converted Staging event.

        Returns:
            dict: _description_
        """
        
        management_api = ManagementAPIStagingModel()

        management_api.populate_properties_from_dict(staging_events)

        # Organization specific processes

        organization_params  = self.organizationalQuerier.getOrganizationParameters_salesforce(
            orgnaization_guid_salesforce=management_api.organization_guid
        )


        # This have to do with building the right interface
        new_details = []
        for event in management_api.details:
            employee_id = event["Actor__c"]

             
            # def __init__(self, event_guid: str, employee_guid: str,  timestamp: datetime, loadbatch_id: int, raw_data: str, operation: str, category: str, application: str, description: str):
            fileEvent = ChromeEvent(
                event_guid=management_api.organization_guid,
                employee_guid=organization_params[employee_id]["employee_guid"],
                timestamp=event["ActionDate__c"],
                loadbatch_id=management_api.guid,
                raw_data=event,
                operation=event["Activity__c"],
                category=event["Object__c"],
                application="SALESFORCE",
                description=event["Description__c"],
                start_time=event["ActionDate__c"],
                end_time=event["ActionDate__c"],
                duration=0,
                title=event["Object__c"],
                url=event["Recor_Link__c"] if "Recor_Link__c" in event else "",
                attachments={},
                action_origin="ACTIVE",
                span_guid="",
                root_reference="",
                root_duration=0,
                root_start = "",
                root_end = "",
            )

            new_details.append(fileEvent.to_dict())

        management_api.details = new_details # Replace with updated interfaces

        return management_api.to_dict()

class TransformationStrategy(ABC):
    """Transformation Strategy to be implemented
    """
    
    @abstractmethod
    def publish(self, enhanced_events: List[dict]):
        pass


    @abstractmethod
    def transform(self, staging_events_events: List[dict]) -> List[dict]: 
        pass


class BasicEnhancement(TransformationStrategy):
    """
    Basic Enhancemnts involves the following:
    (1) Update based on the appropriate source
    (2) Enhance it using the specific business specifications
    (3) Publish it into the events database
    """
    
    def __init__(self, source_adapter, organizationDBProvider: OrganizationalQuerier, publishingDBProvider: DatabaseProvider):
        

        self.organizationDBProvider = organizationDBProvider
        self.publishingDBProvider = publishingDBProvider
        self.default_source_adapter = source_adapter
        
        self.businessRules = {} # To be populated when enhancements is requested.
        


    def transform(self, staging_events_events: List[dict]) -> List[dict]: 
        standarized_events = self.adapt(staging_events_events)
        enhanced_events = self.businessEnhancements(standarized_events)
        return enhanced_events
    

    def businessEnhancements(self, events: dict) -> List[dict]:
        """_summary_

        Args:
            events (dict): _description_

        Returns:
            List[dict]: _description_
        """
        # TODO Business Enhancments (Import the tested and proven business enhancements)
        # Basic Enhancemnets (Assume they it had been already denormalized. )
        normalized_events: List[dict] = ConfigMapper.event_normalization(events)
        print("normalized_events[0]", normalized_events[0]["employee_guid"], "\norganizationDBProvider", self.organizationDBProvider)


        organization_params: List[dict] = self.organizationDBProvider.getOrganizationParameters(normalized_events[0]['employee_guid'])
        joint_events = ConfigMapper.join_organization_fields(
            normalized_events=normalized_events,
            employee_information_table=organization_params
        )
        date_mapped_events = ConfigMapper.date_related_population(join_events=joint_events)

        # Convert into pandas first.
        # date_mapped_events_df = pd.DataFrame(date_mapped_events)
        processed_events = ConfigMapper.categorization_jobs(date_mapped_events=date_mapped_events)
        # processed_events = classified_events_df

        proceesed_json_events = processed_events
        return proceesed_json_events

    def adapt(self, staging_events: dict) -> dict:
        return self.default_source_adapter.adapt(staging_events = staging_events)

    
    def publish(self, enhanced_events: List[dict]):
        self.publishingDBProvider.publish(enhanced_events)

    def fetchBusinessRules():
        """Using the self.organizationDBProvider it receives and updates the Dataset
        """
        pass


class CommonProcessor():
    """Common processor for enhancements, basic transformations into specific interfaces.
    using what it knows about the job type. Receives job parameters from SQS to run those jobs
    
    """
    
    def __init__(self, publishingDBProvider: DatabaseProvider, organization_provider: OrganizationalQuerier, job_parameters: dict):
            
        self.publishingDBProvider = publishingDBProvider
        self.job_parameters = job_parameters
        self.organization_provider = organization_provider
        self.transformation_strategy: TransformationStrategy = self.getTransformationStrategy()

    def runJobs(self):
        """Runs the jobs it was instantiated with.
        """
        events: List[dict] = self.getStagingEvents()
        enhanced_events: List[dict] = self.transformation_strategy.transform(events)
        assert(isinstance(enhanced_events, List))
        self.transformation_strategy.publish(enhanced_events=enhanced_events)

    def getStagingEvents(self) -> List[dict]:
        """Depending on the job parameters it receives the events from either The Provider and either Table.
        I am as
        """
        credentials = {}
        settings = {}
        map_staging_events_source_db = {
            "MOCK_EVENTS": MockStagingDatabaseProviderPrePopulated
        }
        sourceDBProvider = map_staging_events_source_db[self.job_parameters[STAGING_EVENTS_SOURCE]](credentials=credentials, settings=settings)
        staging_event_body = sourceDBProvider.getOne(key_value=self.job_parameters[EVENT_GUID])
        return staging_event_body[DETAILS]


    def getTransformationStrategy(self) -> TransformationStrategy:
        """Understands what type of job to perform depending on the event's type
        """
        
        map_enhancemnettype_TransformationStrategy = {
            'MOCK': BasicEnhancement,
        } #Careful, only one that shouldnt be initialized

        map_source_to_sourceadapter = {
            "MOCK_ADAPTER": MockAdapter,
        }


        transformationStrategyClass = map_enhancemnettype_TransformationStrategy[self.job_parameters[ENHANCEMENT_TYPE]]
        source_adapter_to_use = map_source_to_sourceadapter[self.job_parameters[SOURCE]]
        transformationStrategy = transformationStrategyClass(
            organizationDBProvider=self.organization_provider,
            publishingDBProvider=self.publishingDBProvider,
            source_adapter=source_adapter_to_use()
        )
        return transformationStrategy


    def getTransformationStrategy(self, staging_event) -> TransformationStrategy:
        """Understanding the transformation that is provided by the item. We want to make the transformation later on.
        The idea is toreceive the getTransformationStrategy on the project.

        Returns:
            TransformationStrategy: _description_
        """
        if(staging_event.type == ""):
            pass
        

class BetterCommonProcessor():
    """Fixes:
    - Now it can predict whether is a chrome adapter required or the another by reading teh start of the connector guid. It should actually work
    duty: Receives a simple database provider, and querier. the job parameter accepted is as follows Map<String, String>{event_guid: string}
    """
    def __init__(self, publishingDBProvider: DatabaseProvider, organization_provider: OrganizationalQuerier, job_parameters: dict):
        self.publishingDBProvider = publishingDBProvider
        self.job_parameters = job_parameters

        # Because we dont know how it will look on the future, it would look like { event_guid }
        self.organization_provider = organization_provider

    def runJobs(self):
        """Runs the jobs it was instantiated with. by analizing first which is the job type required
        """
        specific_staging_event: List[dict] = self.getStagingEvent()
        transformationStrategy = self.getTransformationStrategy(specific_staging_event)
        enhanced_events: List[dict] = transformationStrategy.transform(specific_staging_event)
        transformationStrategy.publish(enhanced_events=enhanced_events)

    def getStagingEvent(self) -> List[dict]:
        """Depending on the job parameters it receives the events from either The Provider and either Table.
        I am as
        """
        credentials = {}
        settings = {}

        # But here I am not creating the db at all??
        # sourceDBProvider = map_staging_events_source_db[self.job_parameters[STAGING_EVENTS_SOURCE]](credentials=credentials, settings=settings)
        sourceDBProvider = MockStagingDatabaseProviderWithChrome(credentials=credentials, settings=settings)
        staging_event_body = sourceDBProvider.getOne(key_value=self.job_parameters[EVENT_GUID]) # Gets the first one with that GUID
        return staging_event_body
    
    def getTransformationStrategy(self, staging_event) -> TransformationStrategy:
        """Understanding the transformation that is provided by the item. We want to make the transformation later on.
        The idea is toreceive the getTransformationStrategy on the project.
        """

        # For now I can dummy return Chrom Basic enhancer
        # If connector guid starts with chrome then use Chrome adapter
        
        adapter = ChromeAdapter(organizationQuerier=self.organization_provider)

        if(staging_event[CONNECTOR_GUID].startswith("chrome")):
            adapter = ChromeAdapter(organizationQuerier=self.organization_provider)
        else:
            adapter = SalesforceAdapter(organizationQuerier=self.organization_provider)

        basic_enhancment = BasicEnhancement(
            organizationDBProvider=self.organization_provider,
            publishingDBProvider=self.publishingDBProvider,
            source_adapter=adapter
        )

        return basic_enhancment
        enhanced_events: List[dict] = basic_enhancment.transform(staging_events_events=staging_event)

        return enhanced_events




