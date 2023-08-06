"""Create tool related plugins e.g. conversion_utils"""
from typing import Any
from typing import Dict


def parse(
    hub,
    shared_resource_data: dict,
) -> Dict[str, Any]:
    aws_service_name = shared_resource_data.get("aws_service_name")
    resource_name = shared_resource_data.get("resource_name")

    plugin = {
        "doc": f"Utils related functions for {aws_service_name}.{resource_name}.\n",
        "imports": [
            "import copy",
            "from typing import *",
        ],
        "functions": {
            "convert_raw_resource_to_present_async": hub.pop_create.aws.utils.plugin.generate_convert_raw_to_present(
                resource_name, shared_resource_data["get"]
            ),
        },
    }

    return plugin


def generate_convert_raw_to_present(
    hub, resource_name: str, get_function_definition: dict
):
    return {
        "doc": f"Convert raw resource of {resource_name} type into present format.\n",
        "params": dict(
            idem_resource_name=hub.pop_create.aws.utils.template.NAME_PARAMETER.copy(),
            resource_id=hub.pop_create.aws.utils.template.RESOURCE_ID_PARAMETER.copy(),
            raw_resource=hub.pop_create.aws.utils.template.RAW_RESOURCE_PARAMETER.copy(),
        ),
        "hardcoded": dict(
            **get_function_definition.get("hardcoded", {}),
        ),
    }
