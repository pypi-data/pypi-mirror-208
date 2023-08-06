"""Read & extract service metadata and its available operations"""
import re

import boto3


def parse_resource_and_operations(
    hub, service_name: str, session: "boto3.session.Session"
):
    """
    Get resource and their available operations for client initialized for a given service

    @returns
        Mapping of resource to its methods and corresponding boto3 operation_name.
        {
            "resource": {
                { "method" : "operation_name" }
            }
        }
    """
    operations = {}
    client = session.client(service_name=service_name, region_name="us-west-2")

    for op in client.meta.method_to_api_mapping:
        try:
            verb, resource = op.split("_", maxsplit=1)
            if re.match(rf"\w+[^aoius]s$", resource):
                resource = hub.tool.format.inflect.singular(resource)
            # Special case for resource names that end with apis
            if resource.endswith("apis"):
                resource = resource[:-1]
            if resource not in operations:
                operations[resource] = {}

            if op.endswith(f"{resource}s") and verb.startswith("get"):
                operations[resource]["list"] = op

            if not operations.get(resource, {}).get(verb):
                # do not replace it
                # TODO: Is there a better way to get right methods for a resource?
                operations[resource][verb] = op
        except ValueError:
            hub.log.error("Failure in extracting operation metadata")

    return operations


def parse_docstring(hub, session: "boto3.session.Session", service_name: str):
    """
    Get service description
    """
    client = session.client(service_name=service_name, region_name="us-west-2")
    plugin_docstring = hub.tool.format.html.parse(client._service_model.documentation)
    return "\n".join(hub.tool.format.wrap.wrap(plugin_docstring, width=120))


def parse_service_tag_methods(
    hub, session: "boto3.session.Session", aws_service_name: str
):
    """
    Parses service tag method definitions. There is usually a common method at service level which can be used for
    tagging. Sometimes it is single method for update and sometimes there are separate add/remove methods.
    Capture them all here.
    """
    tag_methods = dict()
    try:
        client = session.client(service_name=aws_service_name, region_name="us-west-2")
        for op in client.meta.method_to_api_mapping:
            if re.match("(add|create|put|tag).*_(resource|tags|tagging)", op):
                tag_methods["tag_resource"] = hub.pop_create.aws.function.parse(
                    session=session,
                    aws_service_name=aws_service_name,
                    resource_name=None,
                    func_name=op,
                )
            elif re.match("(remove|delete|untag).*_(resource|tags|tagging)", op):
                tag_methods["untag_resource"] = hub.pop_create.aws.function.parse(
                    session=session,
                    aws_service_name=aws_service_name,
                    resource_name=None,
                    func_name=op,
                )
            elif re.match("(list|get|describe).*_(tags|tagging)", op):
                tag_methods["list_tags"] = hub.pop_create.aws.function.parse(
                    session=session,
                    aws_service_name=aws_service_name,
                    resource_name=None,
                    func_name=op,
                )
            elif re.match("(change).*_(tags)", op):
                tag_methods["update_tags"] = hub.pop_create.aws.function.parse(
                    session=session,
                    aws_service_name=aws_service_name,
                    resource_name=None,
                    func_name=op,
                )
            else:
                continue
    except Exception as err:
        hub.log.error(
            f"Error when generating tag action definitions for {aws_service_name}: {err.__class__.__name__}: {err}"
        )

    return tag_methods
