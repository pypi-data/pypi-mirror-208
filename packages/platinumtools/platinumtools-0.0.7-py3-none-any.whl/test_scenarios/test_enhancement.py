
from platinumtools.aws_classes.config_mapper_df import *
from platinumtools.aws_classes.class_helpers import *
from platinumtools.aws_classes.class_enhancement import *
from platinumtools.aws_classes.class_adapters import *

sasmple_365_raw_input = {'guid':'fe2cf9f4-5b07-49d6-992d-828c873925e7','version':'1.0','connector_guid':'365_MANAGEMENT','type':'','organization_guid':'8de4e5d3-49de-4b57-a209-organization','actor':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','item_count':5,'details':[{'CreationTime':'2022-10-24T18:23:36','Id':'c878338a-15ff-4986-8bd3-5d6eac071b4a','Operation':'MipLabel','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':43,'UserKey':'c397ec65-e71e-493f-94f2-2e53cdd9b02e','UserType':4,'Version':1,'Workload':'Exchange','ObjectId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','UserId':'nelson@o365.devcooks.com','ApplicationMode':'Standard','ItemName':'HelloThere','LabelAction':'None','LabelAppliedDateTime':'2022-10-25T18:23:32','LabelId':'defa4170-0d19-0005-0004-bc88714345d2','LabelName':'AllEmployees(unrestricted)','Receivers':['nwang@platinumfilings.com','wangnelson2@gmail.com'],'Sender':'nelson@o365.devcooks.com'},{'CreationTime':'2022-10-25T18:23:36','Id':'c17eedb7-6977-4169-b625-bb26e0ede079','Operation':'MipLabel','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':13,'UserKey':'c397ec65-e71e-493f-94f2-2e53cdd9b02e','UserType':4,'Version':1,'Workload':'Exchange','ObjectId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','UserId':'nelson@o365.devcooks.com','IncidentId':'11bb1d67-ae3d-d176-4000-08dab6b85275','PolicyDetails':[{'PolicyId':'00000000-0000-0000-0000-000000000000','Rules':[{'Actions':[],'ConditionsMatched':{'ConditionMatchedInNewScheme':True,'OtherConditions':[{'Name':'SensitivityLabels','Value':'defa4170-0d19-0005-0004-bc88714345d2'}]},'RuleId':'defa4170-0d19-0005-0004-bc88714345d2','RuleMode':'Enable','RuleName':'defa4170-0d19-0005-0004-bc88714345d2','Severity':'Low'}]}],'SensitiveInfoDetectionIsIncluded':False,'ExchangeMetaData':{'BCC':[],'CC':[],'FileSize':17579,'From':'nelson@o365.devcooks.com','MessageID':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','RecipientCount':2,'Sent':'2022-10-25T18:23:33','Subject':'HelloThere','To':['nwang@platinumfilings.com','wangnelson2@gmail.com'],'UniqueID':'fe03264d-a22d-4c70-57b1-08dab6b60675'}},{'CreationTime':'2022-10-25T18:23:33','Id':'e01bd1fb-a635-4f09-57b1-08dab6b60675','Operation':'Send','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':2,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','ClientIP':'68.160.247.154','UserId':'nelson@o365.devcooks.com','AppId':'00000002-0000-0ff1-ce00-000000000000','ClientIPAddress':'68.160.247.154','ClientInfoString':'Client=OWA;Action=ViaProxy','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','SessionId':'e01c84f0-8db1-439e-87bc-5ee52fdf90d4','Item':{'Id':'Unknown','InternetMessageId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','ParentFolder':{'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEPAAAB','Path':'\\Drafts'},'SizeInBytes':3991,'Subject':'HelloThere'}},{'CreationTime':'2022-10-25T18:23:04','Id':'daf566de-6581-486c-b9f7-f8df1d07457f','Operation':'MailItemsAccessed','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':50,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','UserId':'nelson@o365.devcooks.com','AppId':'00000002-0000-0ff1-ce00-000000000000','ClientIPAddress':'68.160.247.154','ClientInfoString':'Client=OWA;Action=ViaProxy','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OperationProperties':[{'Name':'MailAccessType','Value':'Bind'},{'Name':'IsThrottled','Value':'False'}],'OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','SessionId':'e01c84f0-8db1-439e-87bc-5ee52fdf90d4','Folders':[{'FolderItems':[{'InternetMessageId':'<ceafc3fa-fd0a-46ba-9754-e033ee56ce75@az.westcentralus.production.microsoft.com>'},{'InternetMessageId':'<ae042a57-4cd4-466a-adf0-417549c30a96@az.westeurope.production.microsoft.com>'},{'InternetMessageId':'<abccdb15-1bd4-476f-88f8-0bde5349cb61@az.westus2.production.microsoft.com>'},{'InternetMessageId':'<5c06433f-d7f6-48c7-8752-72f5cf93011c@az.westus.production.microsoft.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEMAAAB','Path':'\\Inbox'},{'FolderItems':[{'InternetMessageId':'<CY5PR05MB91439309823940F866A9629EDD2E9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB9143FB7EF878879EED5FC05CDD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB91439292F10817DCB3DE6FC6DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB91436B02DD20921A28720BA4DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB','Path':'\\SentItems'}],'OperationCount':8},{'CreationTime':'2022-10-25T18:23:41','Id':'0d77eaad-2ddd-4e39-8ce1-469113caf263','Operation':'MailItemsAccessed','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':50,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','UserId':'nelson@o365.devcooks.com','AppId':'13937bba-652e-4c46-b222-3003f4d1ff97','ClientAppId':'13937bba-652e-4c46-b222-3003f4d1ff97','ClientIPAddress':'2603:10b6:930:3d::7','ClientInfoString':'Client=REST;Client=RESTSystem;;','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OperationProperties':[{'Name':'MailAccessType','Value':'Bind'},{'Name':'IsThrottled','Value':'False'}],'OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','Folders':[{'FolderItems':[{'InternetMessageId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB','Path':'\\SentItems'}],'OperationCount':1}],'hash_1':'','hash_2':''}
file_interface_adapted_input = {'guid':'fe2cf9f4-5b07-49d6-992d-828c873925e7','version':'1.0','connector_guid':'365_MANAGEMENT','type':'','organization_guid':'8de4e5d3-49de-4b57-a209-organization','actor':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','item_count':5,'details':[{'event_guid':'8de4e5d3-49de-4b57-a209-organization','employee_guid':789012,'timestamp':'2022-10-24T18:23:36','loadbatch_id':'fe2cf9f4-5b07-49d6-992d-828c873925e7','raw_data':{'CreationTime':'2022-10-24T18:23:36','Id':'c878338a-15ff-4986-8bd3-5d6eac071b4a','Operation':'MipLabel','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':43,'UserKey':'c397ec65-e71e-493f-94f2-2e53cdd9b02e','UserType':4,'Version':1,'Workload':'Exchange','ObjectId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','UserId':'nelson@o365.devcooks.com','ApplicationMode':'Standard','ItemName':'HelloThere','LabelAction':'None','LabelAppliedDateTime':'2022-10-25T18:23:32','LabelId':'defa4170-0d19-0005-0004-bc88714345d2','LabelName':'AllEmployees(unrestricted)','Receivers':['nwang@platinumfilings.com','wangnelson2@gmail.com'],'Sender':'nelson@o365.devcooks.com'},'application':'Exchange','operation':'MipLabel','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'8de4e5d3-49de-4b57-a209-organization','employee_guid':789012,'timestamp':'2022-10-25T18:23:36','loadbatch_id':'fe2cf9f4-5b07-49d6-992d-828c873925e7','raw_data':{'CreationTime':'2022-10-25T18:23:36','Id':'c17eedb7-6977-4169-b625-bb26e0ede079','Operation':'MipLabel','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':13,'UserKey':'c397ec65-e71e-493f-94f2-2e53cdd9b02e','UserType':4,'Version':1,'Workload':'Exchange','ObjectId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','UserId':'nelson@o365.devcooks.com','IncidentId':'11bb1d67-ae3d-d176-4000-08dab6b85275','PolicyDetails':[{'PolicyId':'00000000-0000-0000-0000-000000000000','Rules':[{'Actions':[],'ConditionsMatched':{'ConditionMatchedInNewScheme':True,'OtherConditions':[{'Name':'SensitivityLabels','Value':'defa4170-0d19-0005-0004-bc88714345d2'}]},'RuleId':'defa4170-0d19-0005-0004-bc88714345d2','RuleMode':'Enable','RuleName':'defa4170-0d19-0005-0004-bc88714345d2','Severity':'Low'}]}],'SensitiveInfoDetectionIsIncluded':False,'ExchangeMetaData':{'BCC':[],'CC':[],'FileSize':17579,'From':'nelson@o365.devcooks.com','MessageID':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','RecipientCount':2,'Sent':'2022-10-25T18:23:33','Subject':'HelloThere','To':['nwang@platinumfilings.com','wangnelson2@gmail.com'],'UniqueID':'fe03264d-a22d-4c70-57b1-08dab6b60675'}},'application':'Exchange','operation':'MipLabel','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'8de4e5d3-49de-4b57-a209-organization','employee_guid':789012,'timestamp':'2022-10-25T18:23:33','loadbatch_id':'fe2cf9f4-5b07-49d6-992d-828c873925e7','raw_data':{'CreationTime':'2022-10-25T18:23:33','Id':'e01bd1fb-a635-4f09-57b1-08dab6b60675','Operation':'Send','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':2,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','ClientIP':'68.160.247.154','UserId':'nelson@o365.devcooks.com','AppId':'00000002-0000-0ff1-ce00-000000000000','ClientIPAddress':'68.160.247.154','ClientInfoString':'Client=OWA;Action=ViaProxy','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','SessionId':'e01c84f0-8db1-439e-87bc-5ee52fdf90d4','Item':{'Id':'Unknown','InternetMessageId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>','ParentFolder':{'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEPAAAB','Path':'\\Drafts'},'SizeInBytes':3991,'Subject':'HelloThere'}},'application':'Exchange','operation':'Send','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'8de4e5d3-49de-4b57-a209-organization','employee_guid':789012,'timestamp':'2022-10-25T18:23:04','loadbatch_id':'fe2cf9f4-5b07-49d6-992d-828c873925e7','raw_data':{'CreationTime':'2022-10-25T18:23:04','Id':'daf566de-6581-486c-b9f7-f8df1d07457f','Operation':'MailItemsAccessed','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':50,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','UserId':'nelson@o365.devcooks.com','AppId':'00000002-0000-0ff1-ce00-000000000000','ClientIPAddress':'68.160.247.154','ClientInfoString':'Client=OWA;Action=ViaProxy','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OperationProperties':[{'Name':'MailAccessType','Value':'Bind'},{'Name':'IsThrottled','Value':'False'}],'OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','SessionId':'e01c84f0-8db1-439e-87bc-5ee52fdf90d4','Folders':[{'FolderItems':[{'InternetMessageId':'<ceafc3fa-fd0a-46ba-9754-e033ee56ce75@az.westcentralus.production.microsoft.com>'},{'InternetMessageId':'<ae042a57-4cd4-466a-adf0-417549c30a96@az.westeurope.production.microsoft.com>'},{'InternetMessageId':'<abccdb15-1bd4-476f-88f8-0bde5349cb61@az.westus2.production.microsoft.com>'},{'InternetMessageId':'<5c06433f-d7f6-48c7-8752-72f5cf93011c@az.westus.production.microsoft.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEMAAAB','Path':'\\Inbox'},{'FolderItems':[{'InternetMessageId':'<CY5PR05MB91439309823940F866A9629EDD2E9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB9143FB7EF878879EED5FC05CDD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB91439292F10817DCB3DE6FC6DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'},{'InternetMessageId':'<CY5PR05MB91436B02DD20921A28720BA4DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB','Path':'\\SentItems'}],'OperationCount':8},'application':'Exchange','operation':'MailItemsAccessed','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}},{'event_guid':'8de4e5d3-49de-4b57-a209-organization','employee_guid':789012,'timestamp':'2022-10-25T18:23:41','loadbatch_id':'fe2cf9f4-5b07-49d6-992d-828c873925e7','raw_data':{'CreationTime':'2022-10-25T18:23:41','Id':'0d77eaad-2ddd-4e39-8ce1-469113caf263','Operation':'MailItemsAccessed','OrganizationId':'74d25673-b01c-4211-a7c4-9930610fb7eb','RecordType':50,'ResultStatus':'Succeeded','UserKey':'10032002359E261F','UserType':0,'Version':1,'Workload':'Exchange','UserId':'nelson@o365.devcooks.com','AppId':'13937bba-652e-4c46-b222-3003f4d1ff97','ClientAppId':'13937bba-652e-4c46-b222-3003f4d1ff97','ClientIPAddress':'2603:10b6:930:3d::7','ClientInfoString':'Client=REST;Client=RESTSystem;;','ExternalAccess':False,'InternalLogonType':0,'LogonType':0,'LogonUserSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxGuid':'bd6abed2-5d3b-4206-aada-31ca71605e63','MailboxOwnerSid':'S-1-5-21-3007612343-326144747-4028531239-4420872','MailboxOwnerUPN':'nelson@o365.devcooks.com','OperationProperties':[{'Name':'MailAccessType','Value':'Bind'},{'Name':'IsThrottled','Value':'False'}],'OrganizationName':'devcooks.onmicrosoft.com','OriginatingServer':'CY5PR05MB9143(15.20.4200.000)\r\n','Folders':[{'FolderItems':[{'InternetMessageId':'<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>'}],'Id':'LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB','Path':'\\SentItems'}],'OperationCount':1},'application':'Exchange','operation':'MailItemsAccessed','version_source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0},'source_uri':{'id':'','uri':'','file_type':'','file_extension':'','size':0}}],'hash_1':'','hash_2':''}
# interfaced_sample_365 = 
sample_salesforce_raw_input = {
  "guid": "f27ecb0c-975d-dbac-82af-152b68e89902",
  "previous_guid": "91e52161-2a47-7ea4-8121-186f9b378e4a",
  "version": "1.0.0",
  "date": "2023-04-27 16:45:07",
  "connector_guid":"salesforce-testing-connector",
  "organization_guid": "123e4567-e89b-12d3-a456-client",
  "details": [
  {
    "Id": "a1k7c000001fqySAAQ",
    "Name": "0000043628",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:11:10.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqyTAAQ",
    "Name": "0000043632",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:14:18.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqyWAAQ",
    "Name": "0000043627",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:09:28.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqybAAA",
    "Name": "0000043629",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:11:14.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqycAAA",
    "Name": "0000043633",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:14:21.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqylAAA",
    "Name": "0000043631",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:14:14.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqyqAAA",
    "Name": "0000043634",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@platinumfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:18:23.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  }
],
  "hash_1": "d8298e88a929de23ab1bcb06f7a05d0e694f871fb15ef31800d8027d0f76a2ff",
  "hash_2": "3baea71e7edcb8b8aa4417fb640c0fa0d7f9791c8a2b17ca3f499d10f7a43dcd"
}

sample_chrome_raw_input = {
    'guid': '387a26ff-ceed-5015-a6c9-a2cad90329c0',
    'previous_guid': 'b5a496cb-8bfb-39fd-67f2-4d14feef1fa1',
    'version': "1.0.0",
    'date': "2023-05-12 17:50:00.026",
    'connector_guid': "chrome-extension-ddap-1",
    "organization_guid": "organization-1",
    "details":[
  {
    "url": "chrome://extensions/",
    "guid": "bcf17e37-a4b9-17b4-bed2-69aaf120f68c",
    "type": "tab-focus",
    "title": "Extensions",
    "domain": "extensions",
    "params": {},
    "duration": 2,
    "spanId": "3a2a3726-4985-7034-21de-175622df3ed7",
    "endTime": "2023-05-11T16:03:13.783Z",
    "incognito": False,
    "startTime": "2023-05-11T16:03:12.408Z",
    "timestamp": "2023-05-11T16:03:13.408Z"
  },
  
  {
    "id": 16,
    "url": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
    "guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
    "mime": "image/jpeg",
    "type": "download",
    "state": "complete",
    "title": "The Leverage of LLMs for Individuals | TL;DR",
    "danger": "safe",
    "domain": "mazzzystar.github.io",
    "exists": True,
    "paused": False,
    "endTime": "2023-05-11T16:03:31.427Z",
    "fileSize": 72801,
    "filename": "C:\\Users\\NelsonWang\\Downloads\\guide\\superCLUE (2).jpg",
    "finalUrl": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
    "referrer": "https://mazzzystar.github.io/2023/05/10/LLM-for-individual/",
    "canResume": False,
    "incognito": False,
    "startTime": "2023-05-11T16:03:28.431Z",
    "timestamp": "2023-05-11T16:03:31.434Z",
    "totalBytes": 72801,
    "bytesReceived": 72801
  },
  {
    "url": "https://imgbb.com/",
    "guid": "cfe2aea7-dfdf-b8a7-1d55-c870e14fc203",
    "type": "upload",
    "files": [
      {
        "name": "iamge-.jpg",
        "size": 17292,
        "type": "image/jpeg",
        "lastModified": 1683577149679,
        "lastModifiedDate": "2023-05-08T20:19:09.679Z",
        "webkitRelativePath": ""
      }
    ],
    "title": "ImgBB — Upload Image — Free Image Hosting",
    "domain": "imgbb.com",
    "timestamp": "2023-05-11T16:01:02.290Z"
  }
],
    "hash_1": "d8298e88a929de23ab1bcb06f7a05d0e694f871fb15ef31800d8027d0f76a2ff",
    "hash_2": "3baea71e7edcb8b8aa4417fb640c0fa0d7f9791c8a2b17ca3f499d10f7a43dcd"
}

DEBUG = False

def test_business_enhancement():

    organizationDBProvider = MockOrganizationQuerier
    credentials = {}
    settings = {}
    publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)
    # default_source_adapter = MockAdapter()
    
    basic_enhancment = BasicEnhancement(
        organizationDBProvider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider,
        source_adapter=MockAdapter()
    )

    

    res = basic_enhancment.businessEnhancements(events=file_interface_adapted_input)
    if DEBUG: print(res)


def test_365_adapter():
    
    organizationDBProvider = MockOrganizationQuerier
    credentials = {}
    settings = {}
    publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)
    # default_source_adapter = MockAdapter()
    
    basic_enhancment = BasicEnhancement(
        organizationDBProvider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider,
        source_adapter=Microsoft365ManagementAdapter(organizationQuerier=organizationDBProvider)
    )

    res = basic_enhancment.adapt(sasmple_365_raw_input)
    # print(res)
    # print(json.dumps(res))
    # assert(res == file_interface_adapted_input)
    

    # res = basic_enhancment.businessEnhancements(events=file_interface_adapted_input)
    if DEBUG: print(res)
    


def test_365_enhancment_integration():
    """Tests if things can be updated adapted then enhanced then published, no checks
    """
    organizationDBProvider = MockOrganizationQuerier
    credentials = {}
    settings = {}
    publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)

    basic_enhancment = BasicEnhancement(
        organizationDBProvider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider,
        source_adapter=Microsoft365ManagementAdapter(organizationQuerier=organizationDBProvider)
    )

    enhanced_events: List[dict] = basic_enhancment.transform(staging_events_events=sasmple_365_raw_input)
    # basic_enhancment.publish(enhanced_events=enhanced_events)


def test_salesforce_enahncement_integration():
    """Tests if things can be updated adapted then enhanced then published, no checks
    """
    organizationDBProvider = MockOrganizationQuerier
    credentials = {}
    settings = {}
    publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)

    basic_enhancment = BasicEnhancement(
        organizationDBProvider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider,
        source_adapter=SalesforceAdapter(organizationQuerier=organizationDBProvider)
    )

    enhanced_events: List[dict] = basic_enhancment.transform(staging_events_events=sample_salesforce_raw_input)
    # basic_enhancment.publish(enhanced_events=enhanced_events)

def test_chrome_enhancment_integration():
  """Tests if the adapter can be used correctly
  """
  organizationDBProvider = MockOrganizationQuerier
  credentials = {}
  settings = {}
  publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)

  basic_enhancment = BasicEnhancement(
      organizationDBProvider=organizationDBProvider,
      publishingDBProvider=publishingDBProvider,
      source_adapter=ChromeAdapter(organizationQuerier=organizationDBProvider)
  )

  enhanced_events: List[dict] = basic_enhancment.transform(staging_events_events=sample_chrome_raw_input)
  # print(enhanced_events)
  basic_enhancment.publish(enhanced_events=enhanced_events)









