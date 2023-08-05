# https://www.pulumi.com/blog/automatically-enforcing-aws-resource-tagging-policies/

from typing import Dict, Union

import pulumi


def register_auto_tags(auto_tags: Dict[str, str]):
    """Register a stack transformation that automatically adds tags
    to resources that support them
    """
    pulumi.runtime.register_stack_transformation(lambda args: auto_tag(args, auto_tags))


def auto_tag(
    args, auto_tags: Dict[str, str]
) -> Union[pulumi.ResourceTransformationResult, None]:
    """Automatically add tags to resources that support them"""
    if hasattr(args.resource, "tags"):
        if args.type_ not in ("aws-native:eks:Addon"):
            args.props["tags"] = {**(args.props["tags"] or {}), **auto_tags}
        else:
            args.props["tags"] = [
                {"key": k, "value": v}
                for k, v in {**(args.props["tags"] or {}), **auto_tags}.items()
            ]
        return pulumi.ResourceTransformationResult(args.props, args.opts)
    return None
