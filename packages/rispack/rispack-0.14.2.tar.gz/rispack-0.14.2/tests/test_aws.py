import json
import os
import boto3
import pytest
from moto import mock_ssm, mock_secretsmanager, mock_sqs, mock_s3

from rispack.aws import (
    AWS_REGION,
    get_signed_auth,
    get_ssm_parameter,
    put_ssm_parameter,
    get_secret,
    enqueue,
    get_url,
)


@pytest.fixture
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name=AWS_REGION)


@pytest.fixture
def secretsmanager():
    with mock_secretsmanager():
        yield boto3.client("secretsmanager", region_name=AWS_REGION)


@pytest.fixture
def sqs():
    with mock_sqs():
        yield boto3.resource("sqs", region_name=AWS_REGION)


@pytest.fixture
def s3():
    with mock_s3():
        yield boto3.client("s3", region_name=AWS_REGION)


def test_get_signed_auth():
    auth = get_signed_auth()
    assert auth is not None


def test_get_ssm_parameter(ssm):
    ssm.put_parameter(
        Name="test-parameter", Value="test-value", Type="String", Overwrite=True
    )

    value = get_ssm_parameter("test-parameter")
    assert value == "test-value"


def test_put_ssm_parameter(ssm):
    version = put_ssm_parameter(
        "test-parameter", "test-value", param_type="String", overwrite=True
    )

    assert version == 1


def test_get_secret(secretsmanager):
    secretsmanager.create_secret(Name="test-secret", SecretString="test-value")

    value = get_secret("test-secret")
    assert value == "test-value"


def test_enqueue(sqs):
    queue_name = "test-queue"
    queue = sqs.create_queue(QueueName=queue_name)

    message = {"id": 1, "name": "Test message"}
    enqueue(queue_name, message)

    messages = queue.receive_messages()
    assert len(messages) == 1

    message_body = json.loads(json.loads(messages[0].body)["Message"])
    assert message_body == message


def test_get_url(s3):
    bucket_name = "test-bucket"
    object_key = "test/key"
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=b"test-data")

    url = get_url(bucket_name, object_key)
    assert url is not None
