

# Rows as well as indexes might change.

ID_ROW = "id"
USERID_ROW = 'employee_id'
GUID_ROW = "guid"
SOURCEID_ROW = "source_id"
FILENAME_ROW = "filename"
TIMEZONE_ROW = "employee_timezone"
FILEPATH_ROW = "full_path"
EVENTYPE_ROW = "work_hour_type"
SOURCERECORD_ROW = "source_record"
DETERMINATION_ROW = "determination"
PRODSCORE_ROW = "prod_score"
RISKSCORE_ROW = "risk_score"
ACTIONTYPE_ROW = "action_type"
DATEUTC_ROW = "date_utc"
DATE_LOCAL_ROW = "date_local"
COMPUTER_ROW = "computer_id"
USER_ROW='user'
DURATION_ROW = "duration"
TITLE_ROW = "title"
EXECUTABLE = "executable"
DESCRIPTION = "description"
URL_ROW='web_url'
WEBDOMAIN_ROW = "web_domain"
WEBPARAM_ROW = "web_param"
WEBPATH_ROW = "web_path"
PUBLICIP_ROW = "public_ip"
PRIVATEIP_ROW = "private_ip"
APPLICATION_ROW = 'application'
APPLICATIONTYPE_ROW = "application_type"
OPERATIONTYPE_ROW = "operation_type"
OPERATION_ROW = "operation"
ORIGINALOPERATION_ROW = "org_operation"
GROUP_ROW = 'team_id'
MONTH_ROW='month'
MONTHNAME_ROW = "month_name"
WEEKDAY_ROW='weekday_n'
WEEKDAYNAME_ROW = "weekday_name"
YEAR_ROW = 'year'
DAYS_ROW='day'
HOUR_ROW = 'hour'
DATE_ROW='date'
DATETIME_ROW='datetime'
MINUTES_ROW = 'minute'
SECONDS_ROW='seconds'
SUBJECT_ROW = "subject"
RECIPIENTS_ROW = "recipients"
SENDER_ROW = "sender"
CC_ROW = "cc"
BCC_ROW = "bcc"
ATTACHMENTS_ROW = "attachments"
SIZE_ROW = "size"
CALLER_NUMBERS_ROW = "caller_phone_number"
RECIPIENT_NUMBER_ROW = "recipient_phone_number"
CALL_DURATION_ROW = "call_duration"
PROFILE_ROW = "profile_id"
RECORD_NUMBER_ROW="original_identifier"
TIMESLOT_ROW = "time_slot"
ORGANIZATION_ROW = "organization_id"
ISPRODUCTIVE_ROW='determination'
ROW_ORGANIZATION_ID = "organization_id"
EMPLOYEE_ESCAPE_DATES = "employee_escape_dates"
EMPLOYEE_WORK_WEEK_DAYS = "employee_work_days"
EMPLOYEE_GUID = "employee_guid"

ROW_LOG_ID = 'id'
ROW_ACCOUNT_ID = 'organization_id'
ROW_LOG_TYPE = 'source_type'
ROW_PATH = 's3_path'
ROW_MAPPINGBUCKETS = "mapping_buckets"
ROWS_ARR = [ROW_LOG_ID, 'status', ROW_ACCOUNT_ID, ROW_LOG_TYPE, ROW_PATH, 'mapping_instruction', ROW_MAPPINGBUCKETS]
ROWS_STR = ",".join(ROWS_ARR)
NOTFOUND = "null"
ROW_ITEM = "item"
ROW_AFFECTED_ITEMS = "affected_items"
ROW_SUBJECTRE = "subject_re"
ROW_MAIL_PATH = "mailpath"
ROW_ATTACHMENTS = "attachments"
WEEKNUM_ROW = "week"


sql_event_descriptions = {
    GUID_ROW: 'Global Unique Identifier of the event.',
    ORGANIZATION_ROW: 'internal identifier of the organization this events belongs to',
    USERID_ROW: 'internal identifier of the employee this event belongs to.',
    SOURCEID_ROW: 'internal identifier of the original source.',
    PROFILE_ROW: 'internal_identifier of the Profile.',

    USER_ROW: 'Username of the employee this event belong to.',
    TIMEZONE_ROW: 'The timezone of the employee associated with the event.',
    FILEPATH_ROW: 'The Full filepath of the original source file on S3.',
    EVENTYPE_ROW: 'Classification of the employee status (e.g. AFTERHOURS, WORKSHOURS) at the time of event registration in local timezone',
    RECORD_NUMBER_ROW: 'The location (row number) of the event int he original source.',
    DATEUTC_ROW: 'The date of the event in Coordinated Universal Time (UTC).',
    COMPUTER_ROW: 'Identifier of the computer associated with the event.',
    PUBLICIP_ROW: 'The public IP address associated with the event.',
    APPLICATION_ROW: 'The type of application used ot register the event. ( mapping of the type can be configured under bucket settings).',
    ORIGINALOPERATION_ROW: 'The original operation associated with the event.',
    GROUP_ROW: 'The internal identifier of the team associated with the event.',
    SUBJECT_ROW: 'The Subject of the email associated with the event.',
    RECIPIENTS_ROW: 'The Recipients of the email associated with the event.',
    SENDER_ROW: 'The sender of the email associated with the event.',
    CC_ROW: 'The carbon copy (CC) recipients of the email associated with the event.',
    BCC_ROW: 'The blind carbon copy (BCC) recipients of the email associated with the event.',

    WEEKDAYNAME_ROW: 'The short name of hte weekday (e.g. Mon, Tue, Wed) on which the event ocurred.',
    MONTHNAME_ROW: 'The name of the month (e.g. December, January) in which the event occurred.',
    MONTH_ROW: 'The number of the month (e.g. 1 for January, 12 for December) in which the event occurred.',

    WEEKDAY_ROW:'The number of the weekday (e.g. 0 for Monday, 4 for Friday) on which the event occured',
    DAYS_ROW: 'The day of the month on which the event occurred.',
    HOUR_ROW: 'The hour at which the event was registered.',
    MINUTES_ROW: 'The minute on which the event was registered.',
    DATE_ROW: 'The Date on which event was registered.',
    TIMESLOT_ROW: 'The time slot in which the event was registered.',
    WEEKNUM_ROW: 'The week number in which the event was registered (Last week of the year is 52, and 1 for the first week.)',

    DATE_LOCAL_ROW: 'The date of the event in the employee\'s local timezone.',

    APPLICATIONTYPE_ROW: 'The type of application used to register the event',
    OPERATION_ROW: 'The operation type based on the original operation associated with the event (Mappings can be modified at Bucket Settings)',
    ROW_ITEM: 'Items associated with the event',
    ROW_AFFECTED_ITEMS: 'The location (row number) of the affected items associated with the event',
    ROW_SUBJECTRE: 'Subject of the emails associated with the event',
    ROW_MAIL_PATH: 'The mail path (e.g. Inbox, Contacts, Drafts) associated with the event in the operation',
    ROW_ATTACHMENTS: 'Attachemnts associated with the emails associated with the event.',

}



ENHANCEMENT_TYPE = "ENHANCEMNET_TYPE"
ORGANIZATION_GUID = "ORGANIZATION_GUID"
SOURCE = "SOURCE"
STAGING_EVENTS_SOURCE = "STAGING_EVENTS_SOURCE"
EVENT_GUID = "guid"
DETAILS = "details"
CONNECTOR_GUID = "connector_guid"

EVENTS_SAMPLE =  [
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
        ]

STAGING_EVENTS_SAMPLE = [
        {
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
      ]


## Events guids: ["387a26ff-ceed-5015-a6c9-a2cad90329c0", "0adeb6d2-c889-4592-0b46-e43e887e4d71", "cfe2aea7-dfdf-b8a7-1d55-c870e14fc203", "f27ecb0c-975d-dbac-82af-152b68e89902"]

STAGING_EVENTS_SAMPLE_WITH_CHROME = [
       {
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
},
{
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
      ]


from enum import Enum
class EDetermination(Enum):
    WORKHOURS="WORKHOURS"
    AFTERHOURS="AFTERHOURS"
    WEEKENDS = "WEEKENDS"
    DAYOFF="DAYOFF"



