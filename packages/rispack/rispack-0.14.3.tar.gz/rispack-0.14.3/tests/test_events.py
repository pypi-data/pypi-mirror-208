import json
import os
from unittest.mock import patch
from uuid import UUID

import boto3
import pytest

from rispack.errors import EventBusNotSetError
from rispack.events import BaseEvent
from rispack.schemas import dataclass
from moto import mock_sns
from datetime import datetime

@dataclass
class SampleEvent(BaseEvent):
    def __init__(self, aggregate_id: UUID):
        self.aggregate_id = aggregate_id

    def get_type(self):
        return "test"

    def get_version(self):
        return "1"

    def get_aggregate_id(self):
        return self.aggregate_id

def test_publish_event_bus_not_set():
    event = SampleEvent(UUID("3b3ebe16-174a-11ec-9621-0242ac130002"))

    with pytest.raises(EventBusNotSetError):
        event.publish()

@mock_sns
def test_publish_success(aws_credentials):
    os.environ['EVENT_BUS'] = 'test-event-bus'
    event = SampleEvent(UUID("3b3ebe16-174a-11ec-9621-0242ac130002"))

    with patch.object(boto3, "client") as mock_client:
        event.publish()

    mock_client.assert_called_once_with("sns")

    # Extract the message from the SNS publish call
    message = json.loads(mock_client().publish.call_args.kwargs["Message"])

    # Check the message has the expected structure and content
    assert message["id"]
    assert message["origin"] == "rispar.platform"
    assert message["type"] == event.get_type()
    assert message["at"] == datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    assert message["aggregate_id"] == str(event.get_aggregate_id())
    assert message["version"] == event.get_version()
    assert message["payload"] == event.dump()

    # Check the SNS publish call includes the expected parameters
    assert mock_client().publish.call_args.kwargs["TargetArn"] == (
        f"arn:aws:sns:{os.environ['AWS_REGION']}:"
        f"{os.environ['AWS_ACCOUNT_ID']}:{os.environ['EVENT_BUS']}"
    )
    assert mock_client().publish.call_args.kwargs["MessageStructure"] == "string"
    assert mock_client().publish.call_args.kwargs["MessageAttributes"] == {
        "event_type": {"DataType": "String", "StringValue": event.get_type()},
        "event_origin": {"DataType": "String", "StringValue": "rispar.platform"},
    }
