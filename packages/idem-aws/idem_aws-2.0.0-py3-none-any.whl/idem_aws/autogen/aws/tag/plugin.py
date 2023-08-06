"""Parse tags plugin"""
from dict_tools.data import NamespaceDict


def parse(hub, aws_service_name: str, tag_functions: dict):
    """
    Parse tag plugin for the service
    """
    plugin = {
        "doc": f"Tag related functions for AWS service '{aws_service_name}'.",
        "imports": [
            "import copy",
            "from typing import *",
        ],
        "functions": NamespaceDict(
            get_tags_for_resource=hub.pop_create.aws.tag.plugin.generate_get_tags_for_resource(
                tag_functions
            ),
            update_tags=hub.pop_create.aws.tag.plugin.generate_update_tags(
                tag_functions
            ),
        ),
    }

    return plugin


def generate_get_tags_for_resource(hub, tag_functions):
    list_tags_function_definition = tag_functions.get("list_tags", {})
    return {
        "doc": f"Get tags for a given resource.\n",
        "params": dict(
            resource_id=hub.pop_create.aws.tag.template.RESOURCE_ID_PARAMETER.copy(),
        ),
        "hardcoded": dict(
            **list_tags_function_definition.get("hardcoded", {}),
        ),
    }


def generate_update_tags(hub, tag_functions):
    update_tags_function_definition = tag_functions.get("update_tags", {})
    if update_tags_function_definition:
        return {
            "doc": f"Updates tags for a given resource.\n",
            "params": update_tags_function_definition["params"],
            "hardcoded": dict(
                update_tags_boto3_function=update_tags_function_definition.get(
                    "hardcoded", {}
                ).get("boto3_function"),
                update_tags_input_params=update_tags_function_definition.get(
                    "params", {}
                ).keys(),
                single_update=True,
            ),
        }
    else:
        untag_resource_function_definition = tag_functions.get("untag_resource", {})
        tag_resource_function_definition = tag_functions.get("tag_resource", {})
        return {
            "doc": f"Updates tags for a given resource.\n",
            "params": dict(
                resource_id=hub.pop_create.aws.tag.template.RESOURCE_ID_PARAMETER.copy(),
                old_tags=hub.pop_create.aws.tag.template.OLD_TAGS_PARAMETER.copy(),
                new_tags=hub.pop_create.aws.tag.template.NEW_TAGS_PARAMETER.copy(),
            ),
            "hardcoded": dict(
                untag_resource_boto3_function=untag_resource_function_definition.get(
                    "hardcoded", {}
                ).get("boto3_function"),
                untag_resource_input_params=untag_resource_function_definition.get(
                    "params", {}
                ).keys(),
                untag_resource_documentation=untag_resource_function_definition.get(
                    "hardcoded", {}
                ).get("boto3_documentation"),
                tag_resource_boto3_function=tag_resource_function_definition.get(
                    "hardcoded", {}
                ).get("boto3_function"),
                tag_resource_input_params=tag_resource_function_definition.get(
                    "params", {}
                ).keys(),
                tag_resource_documentation=tag_resource_function_definition.get(
                    "hardcoded", {}
                ).get("boto3_documentation"),
                single_update=False,
            ),
        }
