# Testing the Config Mapper

from platinumtools.aws_classes.config_mapper_df import *
from platinumtools.aws_classes.class_helpers import *

DEBUG = False



def check_has_columns(check_columns_exists: List[str], events: List[dict]):
    """Asserts that the events have checks for the columns in the list provided

    Args:
        check_columns_exists (List[str]): List of column names
        events (List[dict]): List of events
    """
    assert(len(events) >= 2)
    for joint_event in events:
        for check_column in check_columns_exists:
            assert(check_column in list(joint_event.keys()))


def test_event_normalization_per_each_detail():
    """Makes sure that the event normalizartion occurs properly
    """
    sample_stagging_event = {
          "guid": "123e4567-e89b-12d3-a456-asdss",
          "version": "1.0",
          "connector_guid": "123e4567-e89b-12d3-a456-client",
          "type": "CHROME_HISTORY",
          "organization_guid": "123e4567-e89b-12d3-a456-1231231",
          "actor": "nwang@abc.com",
          "operation": "SEND_EMAIL",
          "item_count": "2",
          "details": [
            {
                "start_time": "2022-08-15T03:21:45.000Z",
                "end_time": "2022-08-15T03:22:30.000Z",
                "log_duration": 58000,
                "cick_count": 1200,
                "keystroke_count": 22000,
                "application": "Word",
                "event_guid": "qwab-erty-9876-zxcv",
                "employee_guid": "jenkins",
                "source_system": "interactor",
                "timestamp": "2022-08-15T03:22:50.000Z",
                "loadbatc_id": 45,
                "raw_data": "{source.....}"
            },
            {
                "start_time": "2022-08-15T03:23:10.000Z",
                "end_time": "2022-08-15T03:24:00.000Z",
                "log_duration": 62000,
                "cick_count": 900,
                "keystroke_count": 15000,
                "application": "PowerPoint",
                "event_guid": "klop-asd8-mjui-bvcx",
                "employee_guid": "#jenkins",
                "source_system": "interactor",
                "timestamp": "2022-08-15T03:25:10.000Z",
                "loadbatc_id": 78,
                "raw_data": "{source.....}"
            }
        ],
          "hash_1": "d8298e88a929de23ab1bcb06f7a05d0e694f871fb15ef31800d8027d0f76a2ff",
          "hash_2": "3baea71e7edcb8b8aa4417fb640c0fa0d7f9791c8a2b17ca3f499d10f7a43dcd",
          "created_time": "2023-02-21T12:34:56Z"
        }
      
    normalized_events = ConfigMapper.event_normalization(sample_stagging_event)
    if DEBUG: print(normalized_events)
    assert(len(normalized_events) == 2)



def test_join_organizations_fields():

    sample_normalized_events = [{'start_time': '2022-08-15T03:21:45.000Z', 'end_time': '2022-08-15T03:22:30.000Z ', 'log_duration': 58000, 'cick_count': 1200, 'keystroke_count': 22000, 'application': 'Word', 'event_guid': 'qwab-erty-9876-zxcv', 'employee_guid': '#jenkins', 'source_system': 'interactor', 'timestamp': '2022-08-15T03 :22:50.000Z', 'loadbatc_id': 45, 'raw_data': '{source.....}', 'stagging_guid': '123e4567-e89b-12d3-a456-asdss ', 'version': '1.0', 'source_type': 'CHROME_HISTORY', 'actor': 'nwang@abc.com', 'connector_guid': '123e4567-e89b -12d3-a456-client'}, {'start_time': '2022-08-15T03:23:10.000Z', 'end_time': '2022-08-15T03:24:00.000Z', 'log_ duration': 62000, 'cick_count': 900, 'keystroke_count': 15000, 'application': 'PowerPoint', 'event_guid': 'kl op-asd8-mjui-bvcx', 'employee_guid': '#jenkins', 'source_system': 'interactor', 'timestamp': '2022-08-15T03:2 5:10.000Z', 'loadbatc_id': 78, 'raw_data': '{source.....}', 'stagging_guid': '123e4567-e89b-12d3-a456-asdss',  'version': '1.0', 'source_type': 'CHROME_HISTORY', 'actor': 'nwang@abc.com', 'connector_guid': '123e4567-e89b-1 2d3-a456-client'}]
    check_columns_exists = [ ORGANIZATION_ROW, "employee_id", "employee_team_id", "profile_id", "employee_timezone", "employee_guid", "stagging_guid", "employee_work_hours_start", "employee_work_hours_end", "employee_escape_dates", "profile_mapping_instruction", "employee_timezone" ]
    organization_querier = MockOrganizationQuerier
    organization_params: List[dict] = organization_querier.getOrganizationParameters(sample_normalized_events[0]['employee_guid'])

    joint_events = ConfigMapper.join_organization_fields(
        normalized_events=sample_normalized_events, 
        employee_information_table=organization_params
        )
    
    # expected_events = [{'start_time': '2022-08-15T03:21:45.000Z', 'end_time': '2022-08-15T03:22:30.000 Z ', 'log_duration': 58000, 'cick_count': 1200, 'keystroke_count': 22000, 'application': 'Word', 'event_guid' : 'qwab-erty-9876-zxcv', 'employee_guid': '#jenkins', 'source_system': 'interactor', 'timestamp': '2022-08-15 T03 :22:50.000Z', 'loadbatc_id': 45, 'raw_data': '{source.....}', 'stagging_guid': '123e4567-e89b-12d3-a456-a sdss ', 'version': '1.0', 'source_type': 'CHROME_HISTORY', 'actor': 'nwang@abc.com', 'connector_guid': '123e4567 -e89b -12d3-a456-client', 'organization_id': 123456, 'employee_id': 789012, 'employee_team_id': [1, 2, 3], 'p rofile_id': [4, 5, 6], 'employee_timezone': 'America/Los_Angeles', 'employee_work_hours_start': [9, 10, 11, 9, 9, 0, 0], 'employee_work_hours_end': [17, 18, 19, 17, 17, 0, 0], 'employee_escape_dates': ['2022-04-15', '2022-06-10'], 'profile_mapp ing_instruction': {'instruction1': 'value1', 'instruction2': 'value2'}}, {'start_time': '2022-08-15T03:23:10. 000Z', 'end_time': '2022-08-15T03:24:00.000Z', 'log_ duration': 62000, 'cick_count': 900, 'keystroke_count': 15000, 'application': 'PowerPoint', 'event_guid': 'kl op-asd8-mjui-bvcx', 'employee_guid': '#jenkins', 'sourc e_system': 'interactor', 'timestamp': '2022-08-15T03:2 5:10.000Z', 'loadbatc_id': 78, 'raw_data': '{source... ..}', 'stagging_guid': '123e4567-e89b-12d3-a456-asdss', 'version': '1.0', 'source_type': 'CHROME_HISTORY', 'a ctor': 'nwang@abc.com', 'connector_guid': '123e4567-e89b-1 2d3-a456-client', 'organization_id': 123456, 'employe e_id': 789012, 'employee_team_id': [1, 2, 3], 'profile_id': [4, 5, 6], 'employee_timezone': 'America/Los_Ange les', 'employee_work_hours_start': [9, 10, 11, 9, 9, 0, 0], 'employee_work_hours_end': [17, 18, 19, 17, 17, 0, 0], 'employee_escape_dat es': ['2022-04-15', '2022-06-10'], 'profile_mapping_instruction': {'instruction1': 'value1', 'instruction2': 'value2'}}]
    if DEBUG: print(joint_events)
    
    check_has_columns(check_columns_exists, joint_events)

def test_date_related_population():
    sample_joint_events = [{"start_time":"2023-02-27T17:22:50.000Z","end_time":"2023-02-27T17:25:50.000Z","log_duration":58000,"cick_count":1200,"keystroke_count":22000,"application":"Word","event_guid":"qwab-erty-9876-zxcv","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2023-02-27T17:22:50.000Z","loadbatc_id":45,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,10,11],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,18,19],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"}},{"start_time":"2023-02-22T01:22:50.000Z","end_time":"2023-02-22T01:23:50.000Z","log_duration":58000,"cick_count":1200,"keystroke_count":22000,"application":"Word","event_guid":"qwab-erty-9876-zxcv","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2023-02-22T01:22:50.000Z","loadbatc_id":45,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,10,11],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,18,19],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"}},{"start_time":"2023-02-26T03:21:45.000Z","end_time":"2023-02-26T03:23:45.000Z","log_duration":58000,"cick_count":1200,"keystroke_count":22000,"application":"Word","event_guid":"qwab-erty-9876-zxcv","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2023-02-26T17:22:50.000Z","loadbatc_id":45,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,10,11],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,18,19],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"}},{"start_time":"2022-08-15T03:23:10.000Z","end_time":"2022-08-15T03:24:00.000Z","log_duration":62000,"cick_count":900,"keystroke_count":15000,"application":"PowerPoint","event_guid":"klop-asd8-mjui-bvcx","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2022-08-16T03:25:10.000Z","loadbatc_id":78,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,10,11],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,18,19],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"}}]
    
    check_has_columns_exists = [MONTH_ROW, MONTHNAME_ROW, WEEKDAY_ROW, WEEKDAYNAME_ROW, DAYS_ROW, HOUR_ROW, MINUTES_ROW, DATE_ROW, DATE_LOCAL_ROW, TIMESLOT_ROW]
    date_mapped_events = ConfigMapper.date_related_population(sample_joint_events)
    # print(joint_events)
    
    if DEBUG: print(date_mapped_events)

    # Refactoring Resistant test
    check_has_columns(check_columns_exists=check_has_columns_exists,
                      events=date_mapped_events)

def test_bucket_classification():
    # Tests if operations or activity or any others are correctly classified.
    sample_date_events = [{'start_time':'2022-08-15T03:21:45.000Z','end_time':'2022-08-15T03:22:30.000Z','log_duration':58000,'cick_count':1200,'keystroke_count':22000,'application':'Word','event_guid':'qwab-erty-9876-zxcv','employee_guid':'#jenkins','source_system':'interactor','timestamp':'2022-08-15T03:22:50.000Z','loadbatc_id':45,'raw_data':'{source.....}','stagging_guid':'123e4567-e89b-12d3-a456-asdss','version':'1.0','source_type':'CHROME_HISTORY','actor':'nwang@abc.com','connector_guid':'123e4567-e89b-12d3-a456-client','organization_id':123456,'employee_id':789012,'employee_team_id':[1,2,3],'profile_id':[4,5,6],'employee_timezone':'America/Los_Angeles','employee_time_slot_split':6,'employee_work_hours_start':[9,10,11],'employee_work_days':[0,1,2,3,4],'employee_work_hours_end':[17,18,19],'employee_escape_dates':['2022-04-15','2022-06-10'],'profile_mapping_instruction':{'instruction1':'value1','instruction2':'value2'},'month':8,'month_name':'August','weekday_n':6,'weekday_name':'Sun','day':14,'hour':20,'minute':22,'date':'2022-08-14','date_local':'2022-08-14T20:22:50','time_slot':122},{'start_time':'2022-08-15T03:23:10.000Z','end_time':'2022-08-15T03:24:00.000Z','log_duration':62000,'cick_count':900,'keystroke_count':15000,'application':'PowerPoint','event_guid':'klop-asd8-mjui-bvcx','employee_guid':'#jenkins','source_system':'interactor','timestamp':'2022-08-15T03:25:10.000Z','loadbatc_id':78,'raw_data':'{source.....}','stagging_guid':'123e4567-e89b-12d3-a456-asdss','version':'1.0','source_type':'CHROME_HISTORY','actor':'nwang@abc.com','connector_guid':'123e4567-e89b-12d3-a456-client','organization_id':123456,'employee_id':789012,'employee_team_id':[1,2,3],'profile_id':[4,5,6],'employee_timezone':'America/Los_Angeles','employee_time_slot_split':6,'employee_work_hours_start':[9,10,11],'employee_work_days':[0,1,2,3,4],'employee_work_hours_end':[17,18,19],'employee_escape_dates':['2022-04-15','2022-06-10'],'profile_mapping_instruction':{'instruction1':'value1','instruction2':'value2'},'month':8,'month_name':'August','weekday_n':6,'weekday_name':'Sun','day':14,'hour':20,'minute':25,'date':'2022-08-14','date_local':'2022-08-14T20:25:10','time_slot':122}]
    bucket_instructions = {
    "operation": {
        "description": "Bucket that maps into different activity categories: https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema",
        "buckets": {
        "Create": "Create",
        "New-Mailbox": "Create",
        "MipLabel": "Admin",
        "FolderRecycled": "Admin",
        "AddedToGroup": "Admin",
        "SharingPolicyChanged": "Admin",
        "UserLoggedIn": "Login",
        "FolderCreated": "Organize",
        "FolderRenamed": "Organize",
        "FileRenamed": "Organize",
        "GroupAdded": "Organize",
        "FileDownloaded": "Download",
        "FileAccessed": "Read",
        "FilePreviewed": "Read",
        "PageViewed": "Read",
        "FileAccessedExtended": "Read",
        "SoftDelete": "Delete",
        "MoveToDeletedItems": "Delete",
        "HardDelete": "Delete",
        "SearchQueryPerformed": "Search",
        "FileModified": "Update",
        "FileUploaded": "Update",
        "FolderModified": "Update",
        "FileModifiedExtended": "Update"
        }
    },
    "application_type": {
        "description":"Bucket that maps Application Mapper",
        "buckets": {
        "Exchange":"Email",
        "MicrosftTeams": "Chat",
        "Word": "Editor",
        "SharePoint": "Files",
        "OneDrive": "Files",
        "SecurityComplianceCenter": "Authentication",
        "AzureActiveDirectory": "Authentication"
        }
    }
    }

    
    date_mapped_events_df = pd.DataFrame(sample_date_events)

    classified_events: pd.core.frame.DataFrame = ConfigMapper.mapping_application(date_mapped_events_df=date_mapped_events_df, bucket_instructions=bucket_instructions)
    
    classified_dicts = classified_events.to_dict(orient="records")
    if DEBUG: print(classified_dicts)
    
    assert( classified_dicts[0].get(APPLICATIONTYPE_ROW) == "Editor" )

def test_event_classification():
    # Different than the test above, this tests classfications such as 'AFTERHOUR'
    sample_date_events =[{"start_time":"2023-02-27T17:22:50.000Z","end_time":"2023-02-27T17:25:50.000Z","log_duration":58000,"cick_count":1200,"keystroke_count":22000,"application":"Word","event_guid":"qwab-erty-9876-zxcv","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2023-02-27T17:22:50.000Z","loadbatc_id":45,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,9,9,9,9],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,17,17,17,17],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"},"month":2,"month_name":"February","weekday_n":0,"weekday_name":"Mon","day":27,"hour":9,"minute":22,"date":"2023-02-27","date_local":"2023-02-27T09:22:50","time_slot":56},{"start_time":"2023-02-22T03:22:50.000Z","end_time":"2023-02-22T03:23:50.000Z","log_duration":58000,"cick_count":1200,"keystroke_count":22000,"application":"Word","event_guid":"qwab-erty-9876-zxcv","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2023-02-22T03:22:50.000Z","loadbatc_id":45,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,9,9,9,9],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,17,17,17,17],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"},"month":2,"month_name":"February","weekday_n":1,"weekday_name":"Tue","day":21,"hour":17,"minute":22,"date":"2023-02-21","date_local":"2023-02-21T17:22:50","time_slot":104},{"start_time":"2023-02-26T03:21:45.000Z","end_time":"2023-02-26T03:23:45.000Z","log_duration":58000,"cick_count":1200,"keystroke_count":22000,"application":"Word","event_guid":"qwab-erty-9876-zxcv","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2023-02-26T17:22:50.000Z","loadbatc_id":45,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,9,9,9,9],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,17,17,17,17],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"},"month":2,"month_name":"February","weekday_n":6,"weekday_name":"Sun","day":26,"hour":9,"minute":22,"date":"2023-02-26","date_local":"2023-02-26T09:22:50","time_slot":56},{"start_time":"2022-08-15T03:23:10.000Z","end_time":"2022-08-15T03:24:00.000Z","log_duration":62000,"cick_count":900,"keystroke_count":15000,"application":"PowerPoint","event_guid":"klop-asd8-mjui-bvcx","employee_guid":"#jenkins","source_system":"interactor","timestamp":"2022-08-16T03:25:10.000Z","loadbatc_id":78,"raw_data":"{source.....}","stagging_guid":"123e4567-e89b-12d3-a456-asdss","version":"1.0","source_type":"CHROME_HISTORY","actor":"nwang@abc.com","connector_guid":"123e4567-e89b-12d3-a456-client","organization_id":123456,"employee_id":789012,"employee_team_id":[1,2,3],"profile_id":[4,5,6],"employee_timezone":"America/Los_Angeles","employee_time_slot_split":6,"employee_work_hours_start":[9,9,9,9,9],"employee_work_days":[0,1,2,3,4],"employee_work_hours_end":[17,17,17,17,17],"employee_escape_dates":["2022-04-15","2022-06-10"],"profile_mapping_instruction":{"instruction1":"value1","instruction2":"value2"},"month":8,"month_name":"August","weekday_n":0,"weekday_name":"Mon","day":15,"hour":20,"minute":25,"date":"2022-08-15","date_local":"2022-08-15T20:25:10","time_slot":122}]

    date_mapped_events_df = pd.DataFrame(sample_date_events)
    classified_events: pd.core.frame.DataFrame = ConfigMapper.classify_events(date_mapped_events_df=date_mapped_events_df)
    
    classified_dicts = classified_events.to_dict(orient="records")
    
    if True: print(classified_dicts)
    assert( classified_dicts[0].get(EVENTYPE_ROW) == EDetermination.WORKHOURS.value )
    assert( classified_dicts[2].get(EVENTYPE_ROW) ==  EDetermination.WEEKENDS.value )
    assert( classified_dicts[3].get(EVENTYPE_ROW) ==  EDetermination.AFTERHOURS.value )









