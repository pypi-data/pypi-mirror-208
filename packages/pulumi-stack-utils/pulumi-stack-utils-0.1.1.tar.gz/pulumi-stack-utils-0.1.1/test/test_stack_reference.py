# pylint: disable=attribute-defined-outside-init

import json
import os
import random
from datetime import datetime
from unittest import mock

import pytest
from dateutil.tz import tzutc

from pulumi_stack_utils import stack_reference


def mock_download_fileobj(stream):
    """Mock download_fileobj method of S3.Object"""
    latest = random.choice(["latest", "Latest"])
    mock_state = {
        "checkpoint": {
            latest: {
                "resources": [
                    {
                        "type": "pulumi:pulumi:Stack",
                        "outputs": {"test-output": "test-value"},
                    }
                ]
            }
        }
    }
    stream.write(json.dumps(mock_state).encode())


class TestStackReference:
    @mock.patch("boto3.resource")
    def test_get_output(self, mock_s3):
        mock_object = mock.MagicMock()
        mock_object.last_modified = datetime.now(tz=tzutc())
        mock_object.download_fileobj = mock_download_fileobj
        mock_s3.return_value.Object.return_value = mock_object
        stack_name = "test-stack"
        ref = stack_reference.StackReference(
            stack_name, backend_url="s3://test-bucket/test-prefix/"
        )
        output = ref.get_output("test-output")
        assert output == "test-value"

    @mock.patch("boto3.resource")
    def test_read_config(self, mock_s3):
        # change working directory to config directory
        mock_object = mock.MagicMock()
        mock_object.last_modified = datetime.now(tz=tzutc())
        mock_object.download_fileobj = mock_download_fileobj
        mock_s3.return_value.Object.return_value = mock_object
        prev_dir = os.getcwd()
        os.chdir("test/test_config")
        ref = stack_reference.StackReference("test-stack")
        os.chdir(prev_dir)
        output = ref.get_output("test-output")
        assert output == "test-value"

    def test_config_not_found(self):
        with pytest.raises(FileNotFoundError):
            stack_reference.StackReference("test-stack")
