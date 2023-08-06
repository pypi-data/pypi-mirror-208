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

OLD_TAGS_PARAMETER = {
    "default": None,
    "doc": "Dict in the format of {tag-key: tag-value}",
    "param_type": "dict",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

NEW_TAGS_PARAMETER = {
    "default": None,
    "doc": "Dict in the format of {tag-key: tag-value}",
    "param_type": "dict",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}

GET_TAGS_FOR_RESOURCE_REQUEST = """
    result = dict(comment=[], result=True, ret=None)

    if not resource_id:
        result["result"] = False
        result["comment"] = ["resource_id parameter is None"]
        return result

    # DOC: Check boto3 documentation for request syntax: {{ function.hardcoded.boto3_documentation }}
    tags_ret = await hub.exec.boto3.client.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.boto3_function }}(
        ctx,
        # TODO: Map input params with: {{ function.hardcoded.function_input_param_names }}
    )

    if not tags_ret["result"]:
        result["result"] = False
        result["comment"] = tags_ret["comment"]
        return result

    # TODO: Check boto3 documentation for response syntax: {{ function.hardcoded.boto3_documentation }}
    tags = tags_ret.get("ret").get("TODO: <response_key>") if tags_ret.get("result") else None
    result["ret"] = hub.tool.aws.tag_utils.convert_tag_list_to_dict(tags)

    return result
"""

UPDATE_TAGS_REQUEST = """
    result = dict(comment=[], result=True, ret=None)

    tags_to_add = {}
    tags_to_remove = {}
    if new_tags is not None:
        tags_to_remove, tags_to_add = hub.tool.aws.tag_utils.diff_tags_dict(
            old_tags=old_tags, new_tags=new_tags
        )

    if (not tags_to_remove) and (not tags_to_add):
        # If there is nothing to add or remove, return from here with old tags, if present
        result["ret"] = copy.deepcopy(old_tags if old_tags else {})
        return result
    {% if function.hardcoded.single_update %}
        # DOC: Convert tag dict to list with `hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags_to_add)`
        # TODO: Check boto3 documentation for request syntax: {{ function.hardcoded.update_tags_documentation }}
        change_tags_ret = await hub.exec.boto3.client.{{ function.hardcoded.aws_service_name }}.{{ function.hardcoded.update_tags_boto3_function }}(
            ctx,
            # TODO: Map input params with: {{ function.hardcoded.update_tags_input_params }}
        )

        if not change_tags_ret["result"]:
            result["comment"] = change_tags_ret["comment"]
            result["result"] = False
            return result
    {% else %}
    if tags_to_remove:
        if not ctx.get("test", False):
            # DOC: Check boto3 documentation for response syntax: {{ function.hardcoded.untag_resource_documentation }}
            # TODO: Map {{ function.hardcoded.untag_resource_boto3_function }} input params from: {{ function.hardcoded.untag_resource_input_params }}
            delete_ret = await {{ function.hardcoded.untag_resource_boto3_function }}(
                ctx,
                # TODO: Map input params with: {{ function.hardcoded.untag_resource_input_params }}
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result

    if tags_to_add:
        if not ctx.get("test", False):
            # DOC: Check boto3 documentation for response syntax: {{ function.hardcoded.tag_resource_documentation }}
            # TODO: Convert tag dict to list with `hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags_to_add)`
            add_ret = await {{ function.hardcoded.tag_resource_boto3_function }}(
                ctx,
                # TODO: Map input params with: {{ function.hardcoded.tag_resource_input_params }}
            )
            if not add_ret["result"]:
                result["comment"] += add_ret["comment"]
                result["result"] = False
                return result

    result["ret"] = new_tags
    {% endif %}
    if ctx.get("test", False):
        result["comment"] = hub.tool.aws.comment_utils.would_update_tags_comment(
            tags_to_remove=tags_to_remove, tags_to_add=tags_to_add
        )
    else:
        result["comment"] = hub.tool.aws.comment_utils.update_tags_comment(
            tags_to_remove=tags_to_remove, tags_to_add=tags_to_add
        )
    return result
"""
