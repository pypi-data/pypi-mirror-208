"""Build CRUD function definitions for a resource to be used in resource plugins"""
from typing import Any
from typing import Dict


def parse_actions(
    hub,
    session: "boto3.session.Session",
    aws_service_name: str,
    resource_name: str,
    functions: dict,
) -> Dict[str, Any]:
    resource_methods = dict()
    try:
        resource_methods[
            "get"
        ] = hub.pop_create.aws.resource.parse_func_definition_with_possible_names(
            session=session,
            aws_service_name=aws_service_name,
            resource_name=resource_name,
            func_type="describe",
            possible_function_names=hub.pop_create.aws.possible_functions.DESCRIBE_FUNCTIONS,
            aws_functions=functions,
        )

        resource_methods[
            "list"
        ] = hub.pop_create.aws.resource.parse_func_definition_with_possible_names(
            session=session,
            aws_service_name=aws_service_name,
            resource_name=resource_name,
            func_type="describe",
            possible_function_names=hub.pop_create.aws.possible_functions.LIST_FUNCTIONS,
            aws_functions=functions,
        )

        resource_methods[
            "create"
        ] = hub.pop_create.aws.resource.parse_func_definition_with_possible_names(
            session=session,
            aws_service_name=aws_service_name,
            resource_name=resource_name,
            func_type="create",
            possible_function_names=hub.pop_create.aws.possible_functions.CREATE_FUNCTIONS,
            aws_functions=functions,
        )

        resource_methods[
            "delete"
        ] = hub.pop_create.aws.resource.parse_func_definition_with_possible_names(
            session=session,
            aws_service_name=aws_service_name,
            resource_name=resource_name,
            func_type="delete",
            possible_function_names=hub.pop_create.aws.possible_functions.DELETE_FUNCTIONS,
            aws_functions=functions,
        )

        resource_methods[
            "update"
        ] = hub.pop_create.aws.resource.parse_func_definition_with_possible_names(
            session=session,
            aws_service_name=aws_service_name,
            resource_name=resource_name,
            func_type="update",
            possible_function_names=hub.pop_create.aws.possible_functions.UPDATE_FUNCTIONS,
            aws_functions=functions,
        )
    except Exception as err:
        hub.log.error(
            f"Error when generating resource's action definitions for {resource_name}: {err.__class__.__name__}: {err}"
        )

    return resource_methods


def parse_func_definition_with_possible_names(
    hub,
    session: "boto3.session.Session",
    aws_service_name: str,
    resource_name: str,
    func_type: str,
    possible_function_names: list,
    aws_functions: dict,
) -> Dict[str, Any]:
    """
    Create function definitions with possible function names
    """
    possible_func = None
    for func_name in possible_function_names:
        if func_name in aws_functions:
            possible_func = func_name

    if possible_func is None:
        hub.log.info(
            f"Cannot determine function for {func_type} in {aws_service_name}.{resource_name}: {list(aws_functions.keys())}"
        )
        return {}

    return hub.pop_create.aws.function.parse(
        session, aws_service_name, resource_name, aws_functions[possible_func]
    )


def build_resource_init_call(hub, aws_service_name, resource_name):
    """This is generic resource initialization call"""
    return f"resource = await hub.tool.boto3.resource.create(ctx, {aws_service_name}, {resource_name}, resource_id)"


def build_get_by_resource_call(hub):
    """This is to get a resource when generic resource initialization is used"""
    return "await hub.tool.boto3.resource.describe(resource)"
