TAGS_PARAMETER = {
    "default": None,
    "doc": "The tags to apply to the resource. Defaults to None.",
    "param_type": "dict",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

PRESENT_REQUEST_FORMAT = """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False

    desired_state = {
        k: v
        for k, v in locals().items()
        if k not in ("hub", "ctx", "kwargs") and v is not None
    }

    if isinstance(tags, List):
        tags = hub.tool.aws.tag_utils.convert_tag_list_to_dict(tags)

    if resource_id:
        before_ret = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.get(
            ctx,
            name=name,
            resource_id=resource_id,
        )
        if not before_ret["result"] or not before_ret["ret"]:
            result["result"] = False
            result["comment"] = before_ret["comment"]
            return result

        result["old_state"] = copy.deepcopy(before_ret["ret"])
    if before:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state=desired_state
            )
            result["comment"] = (f"Would update aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} '{name}'",)
            return result

        # TODO: Add other required parameters (including tags, if necessary)
        update_ret = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.update(
            ctx,
            name=name,
            resource_id=resource_id,
            # TODO: Add other required parameters (including tags, if necessary): **{{ parameter.mapping.kwargs|default({}) }}
        )

        resource_updated = bool(update_ret["ret"])
        if not resource_updated:
            result["comment"] += (f"'{name}' already exists",)
            result["new_state"] = copy.deepcopy(result["old_state"])
            return result

        result["comment"] += (
            f"Updated aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} '{name}'",
        )
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state=desired_state
            )
            result["comment"] = (f"Would create aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} {name}",)
            return result

        create_ret = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.create(
            ctx,
            name=name,
            resource_id=resource_id,
            # TODO: Add other required parameters from: **{{ parameter.mapping.kwargs|default({})}}
        )
        result["result"] = create_ret["result"]
        if not result["result"]:
            result["comment"] += (create_ret["comment"],)
            return result

        result["comment"] += (f"Created '{name}'",)

        # TODO: extract resource_id from create_ret
        resource_id = create_ret["ret"]["TODO: extract resource_id from the response"]
        # This makes sure the created resource is saved to esm regardless if the subsequent update call fails or not.
        result["new_state"] = {"name": name, "resource_id": resource_id}
        result["comment"] = hub.tool.aws.comment_utils.create_comment(
            resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}", name=name
        )

    # TODO: Add other required parameters
    # Possible parameters: **{{ parameter.mapping.kwargs|default({}) }}
    after = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.get(
        ctx,
        name=name,
        resource_id=resource_id,
    )
    result["new_state"] = after["ret"]
    return result
"""

ABSENT_REQUEST_FORMAT = """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)

    if not resource_id:
        resource_id = (ctx.old_state or {}).get("resource_id")

    # This is to make absent idempotent. If absent is run again, it would be a no-op
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}", name=name
        )
        return result

    # TODO: Add other required parameters
    # Possible parameters: **{{ parameter.mapping.kwargs|default({}) }}
    before_ret = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.get(
        ctx,
        name=name,
        resource_id=resource_id,
    )

    # Case: Error
    if not before_ret["result"]:
        result["result"] = False
        result["comment"] = before_ret["comment"]
        return result

    # Case: Not Found
    if not before_ret["ret"]:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}", name=name
        )
        return result

    if ctx.get("test", False):
        result["old_state"] = before_ret["ret"]
        result["comment"] = (f"Would delete aws.{{ function.hardcoded.service_name }}.{{ function.hardcoded.resource }} '{name}'",)
        return result

    result["old_state"] = before_ret["ret"]

    # TODO: Add other required parameters
    # Possible parameters: **{{ parameter.mapping.kwargs|default({}) }}
    delete_ret = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.delete(
        ctx,
        name=name,
        resource_id=resource_id,
    )

    result["result"] = delete_ret["result"]
    if not result["result"]:
        result["comment"] += (delete_ret["comment"],)
        result["result"] = False
        return result

    result["comment"] = hub.tool.aws.comment_utils.delete_comment(
        resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}", name=name
    )
    return result
"""

DESCRIBE_REQUEST_FORMAT = """
    result = {}

    # TODO: Add other required parameters from: {{ parameter.mapping.kwargs|default({}) }}
    ret = await hub.exec.aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.list(
        ctx
    )

    if not ret or not ret["result"]:
        hub.log.debug(f"Could not describe aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} {ret['comment']}")
        return result

    for resource in ret["ret"]:
        # TODO: Look for respective identifier in **{{ function.hardcoded.resource_attributes }}
        resource_id = resource.get("TODO: Replace with resource identifier")
        result[resource_id] = {
            "aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
"""

GET_REQUEST_FORMAT = """
    result = dict(comment=[], ret=None, result=True)

    # TODO: Map `resource_id` to correct identifier. Check boto3 documentation: {{ function.hardcoded.boto3_documentation }}
    get = await {{ function.hardcoded.boto3_function }}(
        ctx=ctx,
        **{{ parameter.mapping.kwargs|default({}) }}
    )

    # Case: Error
    if not get["result"]:
        # Do not return success=false when it is not found.
        # Most of the resources would return "*NotFound*" type of exception when it is 404
        # TODO: Check NotFound type of exception in boto3 documentation: {{ function.hardcoded.boto3_documentation }}
        if "NotFound" in str(get["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}",
                    name=resource_id
                )
            )
            result["comment"].append(get["comment"])
            return result

        result["comment"].append(get["comment"])
        result["result"] = False
        return result

    # Case: Empty results
    # DOC: Check boto3 documentation for response syntax: {{ function.hardcoded.boto3_documentation }}
    if not get["ret"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}",
                name=resource_id
            )
        )
        return result

    # Case: One matching record is found (If more than one is found, then taking first)
    raw_resource = get["ret"]

    # DOC: Check boto3 documentation for response syntax: {{ function.hardcoded.boto3_documentation }}
    # Resource attributes: {{ function.hardcoded.resource_attributes }}
    result["ret"] = await hub.tool.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}_utils.convert_raw_{{ function.hardcoded.resource_name }}_to_present_async(
        resource_id=resource_id,
        raw_resource=raw_resource,
        tags={},
        idem_resource_name=name,
    )

    return result
"""

LIST_REQUEST_FORMAT = """
    result = dict(comment=[], ret=[], result=True)
    # TODO: Change function methods params if needed
    # DOC: Check boto3 documentation for request syntax: {{ function.hardcoded.boto3_documentation }}
    ret = await {{ function.hardcoded.boto3_function }}(
        ctx=ctx,
        **{{ parameter.mapping.kwargs|default({}) }}
    )

    if not ret["result"]:
        result["comment"].append(ret["comment"])
        result["result"] = False
        return result

    # DOC: Check boto3 documentation for response syntax: {{ function.hardcoded.boto3_documentation }}
    if not ret["ret"].get("{{ function.hardcoded.response_key }}"):
        result["comment"].append(
            hub.tool.aws.comment_utils.list_empty_comment(
                resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}", name=None
            )
        )
        return result

    # boto3 documentation: {{ function.hardcoded.boto3_documentation }}
    for resource in ret["ret"]["{{ function.hardcoded.response_key }}"]:
        # Resource attributes: {{ function.hardcoded.resource_attributes }}
        result["ret"].append(await hub.tool.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}_utils.convert_raw_{{ function.hardcoded.resource_name }}_to_present_async(
            resource_id="TODO: map resource id to correct identifier",
            raw_resource=resource,
            tags={},
            idem_resource_name="TODO: map name to correct response param",
        ))
    return result
"""

CREATE_REQUEST_FORMAT = """
    result = dict(comment=[], ret=[], result=True)

    tags = (
        hub.tool.aws.tag_utils.convert_tag_list_to_dict(tags)
        if isinstance(tags, List)
        else tags
    )

    # TODO: Change function methods params if needed.
    # DOC: Check boto3 documentation for request syntax: {{ function.hardcoded.boto3_documentation }}
    ret = await {{ function.hardcoded.boto3_function }}(
        ctx,
        {{ "ClientToken=name," if function.hardcoded.has_client_token -}}
        **{{ parameter.mapping.kwargs|default({}) }}
    )

    result["result"] = ret["result"]
    if not result["result"]:
        result["comment"].append(ret["comment"])
        return result

    result["comment"].append(f"Created aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} '{name}'",)

    # DOC: Check response syntax in boto3 documentation: {{ function.hardcoded.boto3_documentation }}
    resource_id = result["ret"]["TODO: <resource-id-key>"]

    # TODO: If tags are added as part of create, the following is redundant
    tag_resource_ret = await hub.tool.aws.{{ function.hardcoded.aws_service_name }}.tag.update_tags(
        ctx,
        resource_id=resource_id,
        old_tags={},
        new_tags=tags
    )
    if not tag_resource_ret["result"]:
        result["result"] = False
        result["comment"].append(tag_resource_ret["comment"])

    return result
"""

UPDATE_REQUEST_FORMAT = """
    result = dict(comment=[], ret=[], result=True)

    desired_state = {"name": name, "resource_id": resource_id, **kwargs}

    # DOC: Check boto3 documentation for request syntax: {{ function.hardcoded.boto3_documentation }}
    resource_to_raw_input_mapping = OrderedDict(
    {{ function.hardcoded.function_resource_to_input_param_mappings|pprint|indent(12,true) }}
    )

    parameters_to_update = {}
    for key, value in desired_state.items():
        if key in resource_to_raw_input_mapping.keys() and value is not None:
            parameters_to_update[resource_to_raw_input_mapping[key]] = desired_state.get(key)

    if parameters_to_update:
        ret = await {{ function.hardcoded.boto3_function }}(
            ctx,
            {{ "ClientToken=name," if function.hardcoded.has_client_token -}}
            **parameters_to_update
        )

        if not ret["result"]:
            result["result"] = False
            result["comment"] += (
                f"Could not update aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} '{name}'",
            )
            result["comment"].append(ret["comment"])
            return result

        result["comment"].append(f"Updated aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }} '{name}'",)

        # TODO: If tags are updated as part of update function then the following tag update is redundant
        get_tags_ret = await hub.tool.aws.{{ function.hardcoded.aws_service_name }}.tag.get_tags_for_resource(
            ctx,
            resource_id=resource_id
        )

        if get_tags_ret["result"]:
            current_tags = get_tags_ret.get("ret", {})
            tags = kwargs.get("tags", {})
            tags = (
                hub.tool.aws.tag_utils.convert_tag_list_to_dict(tags)
                if isinstance(tags, List)
                else tags
            )
            update_tags_ret = await hub.tool.aws.{{ function.hardcoded.aws_service_name }}.tag.update_tags(
                ctx,
                resource_id=resource_id,
                old_tags=current_tags,
                new_tags=tags
            )
            if not update_tags_ret["result"]:
                result["result"] = False
                result["comment"] += update_tags_ret["comment"]
                return result
    return result
"""

DELETE_REQUEST_FORMAT = """
    result = dict(comment=[], ret=[], result=True)

    # Check boto3 documentation for inputs: {{ function.hardcoded.boto3_documentation }}
    delete_ret = await {{ function.hardcoded.boto3_function }}(
        ctx,
        {{ "ClientToken=name," if function.hardcoded.has_client_token -}}
        **{{ parameter.mapping.kwargs|default({}) }}
    )

    result["result"] = delete_ret["result"]

    if not result["result"]:
        result["comment"] = delete_ret["comment"]
        result["result"] = False
        return result

    result["comment"] = hub.tool.aws.comment_utils.delete_comment(
        resource_type="aws.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.resource_name }}", name=name
    )

    return result
"""
