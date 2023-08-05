import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import boto3
import yaml
from dateutil.tz import tzutc


class StackReference:
    """Object referencing the state of a Pulumi stack in S3"""

    def __init__(self, stack_name: str, backend_url: str = None):  # type: ignore
        self.stack_name = stack_name
        self._outputs: dict = {}

        if backend_url is None:
            project_config_path = Path("Pulumi.yaml")
            if not project_config_path.exists():
                msg = """
                    Could not determine location of state backend.
                    Please specify a backend_url
                """
                raise FileNotFoundError(msg)

            with open(project_config_path, "r", encoding="utf-8") as f:
                project_config = yaml.safe_load(f)
                backend_url = project_config["backend"]["url"]

        if not backend_url.endswith("/"):
            backend_url += "/"

        bucket_name, prefix = backend_url.split("/", 3)[2:]
        key = str(Path(prefix).joinpath(".pulumi", "stacks", f"{stack_name}.json"))
        s3 = boto3.resource("s3")
        self._state_object = s3.Object(bucket_name, key)
        print(type(self._state_object))
        self.stack_last_modified: datetime = datetime(2000, 1, 1, tzinfo=tzutc())

    @property
    def outputs(self) -> dict:
        """The outputs of the stack"""
        last_modified = self.state_object.last_modified
        if last_modified > self.stack_last_modified:
            self.stack_last_modified = last_modified
            state = self.download_state()

            # Different versions of pulumi use different keys for the latest checkpoint
            latest = "latest" if "latest" in state["checkpoint"] else "Latest"

            outputs = {}
            for resource in state["checkpoint"][latest]["resources"]:
                if resource["type"] == "pulumi:pulumi:Stack":
                    outputs = resource["outputs"]
                    break
            self._outputs = outputs
        return self._outputs

    @property
    def state_object(self):
        """The state object for the stack"""
        self._state_object.reload()
        return self._state_object

    def download_state(self) -> dict:
        """Download the outputs from the state backend"""
        stream = BytesIO()
        self.state_object.download_fileobj(stream)
        state = json.loads(stream.getvalue().decode("utf-8"))
        return state

    def get_output(self, output_name: str) -> Any:
        """Retrieve a stack output by name"""
        return self.outputs.get(output_name)
