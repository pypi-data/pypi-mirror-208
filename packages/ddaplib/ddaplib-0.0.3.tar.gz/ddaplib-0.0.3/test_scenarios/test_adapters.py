from platinumtools.aws_classes.config_mapper_df import *
from platinumtools.aws_classes.class_helpers import *
from platinumtools.aws_classes.class_adapters import *
import json

test_input = [
    {
      "CreationTime": "2022-10-24T18:23:36",
      "Id": "c878338a-15ff-4986-8bd3-5d6eac071b4a",
      "Operation": "MipLabel",
      "OrganizationId": "74d25673-b01c-4211-a7c4-9930610fb7eb",
      "RecordType": 43,
      "UserKey": "c397ec65-e71e-493f-94f2-2e53cdd9b02e",
      "UserType": 4,
      "Version": 1,
      "Workload": "Exchange",
      "ObjectId": "<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>",
      "UserId": "nelson@o365.devcooks.com",
      "ApplicationMode": "Standard",
      "ItemName": "Hello There",
      "LabelAction": "None",
      "LabelAppliedDateTime": "2022-10-25T18:23:32",
      "LabelId": "defa4170-0d19-0005-0004-bc88714345d2",
      "LabelName": "All Employees (unrestricted)",
      "Receivers": ["nwang@platinumfilings.com", "wangnelson2@gmail.com"],
      "Sender": "nelson@o365.devcooks.com"
    },
    {
      "CreationTime": "2022-10-25T18:23:36",
      "Id": "c17eedb7-6977-4169-b625-bb26e0ede079",
      "Operation": "MipLabel",
      "OrganizationId": "74d25673-b01c-4211-a7c4-9930610fb7eb",
      "RecordType": 13,
      "UserKey": "c397ec65-e71e-493f-94f2-2e53cdd9b02e",
      "UserType": 4,
      "Version": 1,
      "Workload": "Exchange",
      "ObjectId": "<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>",
      "UserId": "nelson@o365.devcooks.com",
      "IncidentId": "11bb1d67-ae3d-d176-4000-08dab6b85275",
      "PolicyDetails": [
        {
          "PolicyId": "00000000-0000-0000-0000-000000000000",
          "Rules": [
            {
              "Actions": [],
              "ConditionsMatched": {
                "ConditionMatchedInNewScheme": True,
                "OtherConditions": [
                  {
                    "Name": "SensitivityLabels",
                    "Value": "defa4170-0d19-0005-0004-bc88714345d2"
                  }
                ]
              },
              "RuleId": "defa4170-0d19-0005-0004-bc88714345d2",
              "RuleMode": "Enable",
              "RuleName": "defa4170-0d19-0005-0004-bc88714345d2",
              "Severity": "Low"
            }
          ]
        }
      ],
      "SensitiveInfoDetectionIsIncluded": False,
      "ExchangeMetaData": {
        "BCC": [],
        "CC": [],
        "FileSize": 17579,
        "From": "nelson@o365.devcooks.com",
        "MessageID": "<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>",
        "RecipientCount": 2,
        "Sent": "2022-10-25T18:23:33",
        "Subject": "Hello There",
        "To": ["nwang@platinumfilings.com", "wangnelson2@gmail.com"],
        "UniqueID": "fe03264d-a22d-4c70-57b1-08dab6b60675"
      }
    },
    {
      "CreationTime": "2022-10-25T18:23:33",
      "Id": "e01bd1fb-a635-4f09-57b1-08dab6b60675",
      "Operation": "Send",
      "OrganizationId": "74d25673-b01c-4211-a7c4-9930610fb7eb",
      "RecordType": 2,
      "ResultStatus": "Succeeded",
      "UserKey": "10032002359E261F",
      "UserType": 0,
      "Version": 1,
      "Workload": "Exchange",
      "ClientIP": "68.160.247.154",
      "UserId": "nelson@o365.devcooks.com",
      "AppId": "00000002-0000-0ff1-ce00-000000000000",
      "ClientIPAddress": "68.160.247.154",
      "ClientInfoString": "Client=OWA;Action=ViaProxy",
      "ExternalAccess": False,
      "InternalLogonType": 0,
      "LogonType": 0,
      "LogonUserSid": "S-1-5-21-3007612343-326144747-4028531239-4420872",
      "MailboxGuid": "bd6abed2-5d3b-4206-aada-31ca71605e63",
      "MailboxOwnerSid": "S-1-5-21-3007612343-326144747-4028531239-4420872",
      "MailboxOwnerUPN": "nelson@o365.devcooks.com",
      "OrganizationName": "devcooks.onmicrosoft.com",
      "OriginatingServer": "CY5PR05MB9143 (15.20.4200.000)\r\n",
      "SessionId": "e01c84f0-8db1-439e-87bc-5ee52fdf90d4",
      "Item": {
        "Id": "Unknown",
        "InternetMessageId": "<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>",
        "ParentFolder": {
          "Id": "LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEPAAAB",
          "Path": "\\Drafts"
        },
        "SizeInBytes": 3991,
        "Subject": "Hello There"
      }
    },
    {
      "CreationTime": "2022-10-25T18:23:04",
      "Id": "daf566de-6581-486c-b9f7-f8df1d07457f",
      "Operation": "MailItemsAccessed",
      "OrganizationId": "74d25673-b01c-4211-a7c4-9930610fb7eb",
      "RecordType": 50,
      "ResultStatus": "Succeeded",
      "UserKey": "10032002359E261F",
      "UserType": 0,
      "Version": 1,
      "Workload": "Exchange",
      "UserId": "nelson@o365.devcooks.com",
      "AppId": "00000002-0000-0ff1-ce00-000000000000",
      "ClientIPAddress": "68.160.247.154",
      "ClientInfoString": "Client=OWA;Action=ViaProxy",
      "ExternalAccess": False,
      "InternalLogonType": 0,
      "LogonType": 0,
      "LogonUserSid": "S-1-5-21-3007612343-326144747-4028531239-4420872",
      "MailboxGuid": "bd6abed2-5d3b-4206-aada-31ca71605e63",
      "MailboxOwnerSid": "S-1-5-21-3007612343-326144747-4028531239-4420872",
      "MailboxOwnerUPN": "nelson@o365.devcooks.com",
      "OperationProperties": [
        { "Name": "MailAccessType", "Value": "Bind" },
        { "Name": "IsThrottled", "Value": "False" }
      ],
      "OrganizationName": "devcooks.onmicrosoft.com",
      "OriginatingServer": "CY5PR05MB9143 (15.20.4200.000)\r\n",
      "SessionId": "e01c84f0-8db1-439e-87bc-5ee52fdf90d4",
      "Folders": [
        {
          "FolderItems": [
            {
              "InternetMessageId": "<ceafc3fa-fd0a-46ba-9754-e033ee56ce75@az.westcentralus.production.microsoft.com>"
            },
            {
              "InternetMessageId": "<ae042a57-4cd4-466a-adf0-417549c30a96@az.westeurope.production.microsoft.com>"
            },
            {
              "InternetMessageId": "<abccdb15-1bd4-476f-88f8-0bde5349cb61@az.westus2.production.microsoft.com>"
            },
            {
              "InternetMessageId": "<5c06433f-d7f6-48c7-8752-72f5cf93011c@az.westus.production.microsoft.com>"
            }
          ],
          "Id": "LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEMAAAB",
          "Path": "\\Inbox"
        },
        {
          "FolderItems": [
            {
              "InternetMessageId": "<CY5PR05MB91439309823940F866A9629EDD2E9@CY5PR05MB9143.namprd05.prod.outlook.com>"
            },
            {
              "InternetMessageId": "<CY5PR05MB9143FB7EF878879EED5FC05CDD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>"
            },
            {
              "InternetMessageId": "<CY5PR05MB91439292F10817DCB3DE6FC6DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>"
            },
            {
              "InternetMessageId": "<CY5PR05MB91436B02DD20921A28720BA4DD2D9@CY5PR05MB9143.namprd05.prod.outlook.com>"
            }
          ],
          "Id": "LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB",
          "Path": "\\Sent Items"
        }
      ],
      "OperationCount": 8
    },
    {
      "CreationTime": "2022-10-25T18:23:41",
      "Id": "0d77eaad-2ddd-4e39-8ce1-469113caf263",
      "Operation": "MailItemsAccessed",
      "OrganizationId": "74d25673-b01c-4211-a7c4-9930610fb7eb",
      "RecordType": 50,
      "ResultStatus": "Succeeded",
      "UserKey": "10032002359E261F",
      "UserType": 0,
      "Version": 1,
      "Workload": "Exchange",
      "UserId": "nelson@o365.devcooks.com",
      "AppId": "13937bba-652e-4c46-b222-3003f4d1ff97",
      "ClientAppId": "13937bba-652e-4c46-b222-3003f4d1ff97",
      "ClientIPAddress": "2603:10b6:930:3d::7",
      "ClientInfoString": "Client=REST;Client=RESTSystem;;",
      "ExternalAccess": False,
      "InternalLogonType": 0,
      "LogonType": 0,
      "LogonUserSid": "S-1-5-21-3007612343-326144747-4028531239-4420872",
      "MailboxGuid": "bd6abed2-5d3b-4206-aada-31ca71605e63",
      "MailboxOwnerSid": "S-1-5-21-3007612343-326144747-4028531239-4420872",
      "MailboxOwnerUPN": "nelson@o365.devcooks.com",
      "OperationProperties": [
        { "Name": "MailAccessType", "Value": "Bind" },
        { "Name": "IsThrottled", "Value": "False" }
      ],
      "OrganizationName": "devcooks.onmicrosoft.com",
      "OriginatingServer": "CY5PR05MB9143 (15.20.4200.000)\r\n",
      "Folders": [
        {
          "FolderItems": [
            {
              "InternetMessageId": "<CY5PR05MB9143EE143E6008D69C9391F5DD319@CY5PR05MB9143.namprd05.prod.outlook.com>"
            }
          ],
          "Id": "LgAAAAALcWhVmnTeRJS8qp8HxA25AQC/yWJ3KK0XQJ7UyikjUZtEAAAAAAEJAAAB",
          "Path": "\\Sent Items"
        }
      ],
      "OperationCount": 1
    }
  ]

def test_audit_365_to_socket():
    # print("Entering rawAPIBodies", test_input)
    organization_querier = MockOrganizationQuerier

    res = Audit365ToSocketAdaptor.transform(organization_querier=organization_querier, rawAPIBodies=test_input)

    
    print(res)
    # print(json.dumps(res))




















