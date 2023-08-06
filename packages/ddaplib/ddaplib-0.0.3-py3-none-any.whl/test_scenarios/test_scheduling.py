
from abc import ABC, abstractmethod
from typing import List
from platinumtools.aws_classes.class_helpers import *
from platinumtools.aws_classes.class_scheduling import *


def test_single_sqs_scheduler():

    mockDBProvider = MockDatabaseProvider(credentials={}, settings={})
    data_received = [

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
    single_scheduler = SingleSQSJobScheduler(
        rawPublishinStrategies=[mockDBProvider],
        sqs_enpoint="https://sqs.us-east-1.amazonaws.com/796522278827/MockQueue.fifo"
        )
    
    
    single_scheduler.publishRaw(events=data_received) #Should print the event that is being publsihed
    single_scheduler.scheduleJob(events=data_received) #Should actually schedule the job.
    
    assert(len(mockDBProvider.db)>=1)


def test_integration_sqs_scheduler_postgresqProvider():
    """You still have to manually check the postgres database to see if it was actually modified.
    """
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
    dbProvider = PostgreSQLProvider(credentials=credentials, settings=settings)
    random_identifier = Utils.createRandomStr()
    data_received = [

        {
        "guid": "123e4567-e89b-12d3-a456-"+random_identifier,
        "version": "1.0",
        "source_guid": "2023-02-21T12:34:56Z",
        "type": "MOCK_TYPE",
        "organization_guid": "org123",
        "employee_guid": "123e4567-e89b-12d3-a456-426655440000",
        "operation": "MOCK_OPERATION",
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
    single_scheduler = SingleSQSJobScheduler(
        rawPublishinStrategies=[dbProvider],
        sqs_enpoint="https://sqs.us-east-1.amazonaws.com/796522278827/MockQueue.fifo"
        )
    
    
    single_scheduler.publishRaw(events=data_received) #Should print the event that is being publsihed
    single_scheduler.scheduleJob(events=data_received) #Should actually schedule the job.
    
    # assert(len(mockDBProvider.db)>=1)

