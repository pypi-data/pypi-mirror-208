NAME_PARAMETER = {
    "default": None,
    "doc": "An Idem name of the resource",
    "param_type": "str",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

RESOURCE_ID_PARAMETER = {
    "default": None,
    "doc": "An identifier of the resource in the provider",
    "param_type": "str",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

RAW_RESOURCE_PARAMETER = {
    "default": None,
    "doc": "The raw representation of the resource in the provider",
    "param_type": "dict",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

CONVERT_RAW_RESOURCE_TO_PRESENT_REQUEST = """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id
    }

    resource_parameters = OrderedDict(
    {{ function.hardcoded.raw_resource_to_resource_mapping|pprint|indent(12,true) }}
    )

    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource and raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    # Get it from raw_resource or explicitly retrieved tags
    resource_tags_list = raw_resource.get("Tags") or raw_resource.get("TagList")

    if resource_tags_list:
        resource_translated["tags"] = hub.tool.aws.tag_utils.convert_tag_list_to_dict(
            resource_tags_list
        )
    else:
        resource_translated["tags"] = await hub.tool.aws.{{ function.hardcoded.aws_service_name }}.tag.get_tags_for_resource(
            ctx,
            resource_id=resource_id
        )

    return resource_translated
"""
