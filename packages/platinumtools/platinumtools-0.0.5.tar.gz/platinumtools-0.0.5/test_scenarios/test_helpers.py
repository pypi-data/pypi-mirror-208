
from platinumtools.aws_classes.class_helpers import *
COLUMN_BODY = "body"
COLUMN_KEY = "key"


def test_postgresql_provider_publishes():
    credentials = {
        'USERNAME': "postgres",
        'PASSWORD': "dDueller123araM=!",
        "HOST": "test-ddanalytics-rds-v2.cpcwi20k2qgg.us-east-1.rds.amazonaws.com",
        "DB": "v1_2"
    }

    settings = {
        "TABLENAME": "people_table_sample",
        "COLUMN_NAMES": ["name", "age", "gender"],
    }

    pgProvider = PostgreSQLProvider(credentials=credentials, settings=settings)

    data = [
        {"name": "Alice", "age": 25, "gender": "F"},
        {"name": "Bob", "age": 30, "gender": "M"},
        {"name": "Charlie", "age": 35, "gender": "M"}
    ]

    pgProvider.publish(data)


def test_postgresql_provider_get_one():
    
    credentials = {
        'USERNAME': "postgres",
        'PASSWORD': "dDueller123araM=!",
        "HOST": "test-ddanalytics-rds-v2.cpcwi20k2qgg.us-east-1.rds.amazonaws.com",
        "DB": "v1_2"
    }

    settings = {
        "TABLENAME": "people_table_sample",
    }

    
    pgProvider = PostgreSQLProvider(credentials=credentials, settings=settings)
    res = pgProvider.getOne( key_value="Alice", key_column="name")

    assert(isinstance(res, dict)) # Is Dictionary Instance
    assert(res == {'age': 25, 'gender': 'F', 'name': 'Alice'})


def test_escapedStrToListOfObjects_basic_list_str():

    input_string = '[         {\"name\": \"Alice\", \"age\": 25, \"gender\": \"F\"},         {\"name\": \"Bob\", \"age\": 30, \"gender\": \"M\"},         {\"name\": \"Charlie\", \"age\": 35, \"gender\": \"M\"}     ]'
    expected_result = [{'name': 'Alice', 'age': 25, 'gender': 'F'}, {'name': 'Bob', 'age': 30, 'gender':
 'M'}, {'name': 'Charlie', 'age': 35, 'gender': 'M'}]
    assert(Utils.escapedStrToListOfObjects(input_string) == expected_result)


def test_escapedStrToListOfObjects_empty_str():
    """Conclusions:
    '' => [] Or it might cause trouble
    """
    input_string = ''
    expected_result = []
    # print("Results in", Utils.escapedStrToListOfObjects(input_string))
    assert(Utils.escapedStrToListOfObjects(input_string) == expected_result)


def test_postgresql_provider_publishes_complex_event():
    credentials = {
        'USERNAME': "postgres",
        'PASSWORD': "dDueller123araM=!",
        "HOST": "test-ddanalytics-rds-v2.cpcwi20k2qgg.us-east-1.rds.amazonaws.com",
        "DB": "v1_2"
    }

    settings = {
        "TABLENAME": "staging_events",
        "COLUMN_NAMES": ["guid", "version", "source_guid", "type", "organization_guid", "employee_guid", "operation", "item_count", "details", "hash_1", "hash_2", "created_time"],
    }

    pgProvider = PostgreSQLProvider(credentials=credentials, settings=settings)

    data = [
        {
        "guid": "123e4567-e89b-12d3-a456-426655440000",
        "version": "1.0",
        "source_guid": "2023-02-21T12:34:56Z",
        "type": "Chrome History",
        "organization_guid": "org123",
        "employee_guid": "123e4567-e89b-12d3-a456-426655440000",
        "operation": "send email",
        "item_count": "3",
        "details": [
            {
            "start_time": "2018-09-18T09:24:03.000Z",
            "end_time": "2018-09-18T09:25:00.000Z",
            "log_duration": 60000,
            "cick_count": 1000,
            "keystroke_count": 23000,
            "application": "Excel",
            "event_id": "urgh-asd9-numf-quad",
            "user_id": "#idnelson",
            "source_system": "Zoom",
            "timestamp": "2018-09-18T09:25:03.000Z",
            "loadbatc_id": 23,
            "raw_data": "{source…..}"
            },              
            {
            "start_time": "2018-09-18T09:24:03.000Z",
            "end_time": "2018-09-18T09:25:00.000Z",
            "log_duration": 60000,
            "cick_count": 1000,
            "keystroke_count": 23000,
            "application": "Excel",
            "event_id": "urgh-asd9-numf-quad",
            "user_id": "#idnelson",
            "source_system": "Zoom",
            "timestamp": "2018-09-18T09:25:03.000Z",
            "loadbatc_id": 23,
            "raw_data": "{source…..}"
            }
        ],
        "hash_1": "d8298e88a929de23ab1bcb06f7a05d0e694f871fb15ef31800d8027d0f76a2ff",
        "hash_2": "3baea71e7edcb8b8aa4417fb640c0fa0d7f9791c8a2b17ca3f499d10f7a43dcd",
        "created_time": "2023-02-21T12:34:56Z"
        }
    ]

    pgProvider.publish(data)

