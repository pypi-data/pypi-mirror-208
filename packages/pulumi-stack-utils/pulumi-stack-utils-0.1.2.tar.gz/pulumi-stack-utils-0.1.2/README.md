# pulumi-stack-utils
![test workflow](https://github.com/rs21io/pulumi-stack-utils/actions/workflows/test.yml/badge.svg)

A collection of utilities for working with [Pulumi](https://pulumi.com) stacks

The original motivation for this package is to get around some limitations with the `StackReference`
available in the official [pulumi](https://pypi.org/project/pulumi/) Python package. Specifically around
reading outputs from other stacks. Currently, stacks need to share the same passphrase to read outputs
from each other, even if the output isn't secret.

More information can be found in [this issue](https://github.com/pulumi/pulumi/issues/2823).

## Installation

```bash
pip install pulumi-stack-utils
```

## Usage

Retrieve outputs from a stack using an S3 backend

```python
from pulumi_stack_utils import StackReference

# If backend_url isn't provided the package will try and read it
# from the Pulumi.yaml file in the cwd
ref = StackReference("project/my-stack", backend_url="s3://state-backend/prefix")
output = ref.get_output("myOutput")
```

Autotag resources created on AWS. Based on this [blog post](https://www.pulumi.com/blog/automatically-enforcing-aws-resource-tagging-policies/)

```python
import pulumi
from pulumi_stack_utils.aws.autotag import register_auto_tags

config = pulumi.config()
register_auto_tags({
    "user:Project": pulumi.get_project(),
    "user:Stack": pulumi.get_stack(),
    "user:Owner": config.require("stackOwner"),
})
```
