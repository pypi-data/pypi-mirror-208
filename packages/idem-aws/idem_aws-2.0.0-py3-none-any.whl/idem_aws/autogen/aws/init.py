import pathlib

import boto3.session
from dict_tools.data import NamespaceDict

try:
    import tqdm

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def __init__(hub):
    hub.pop.sub.load_subdirs(hub.pop_create.aws)


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)
    ctx.servers = [None]

    # AWS already has an acct plugin
    ctx.has_acct_plugin = False
    ctx.service_name = "aws_auto"

    # Now start getting into AWS resource plugin creation
    session = boto3.session.Session()

    # If CLI provides services then use those services first
    # e.g. --services rds
    services = hub.OPT.pop_create.services or session.get_available_services()
    # This takes a while because we are making http calls to aws
    for aws_service_name in tqdm.tqdm(services, desc="services"):
        # Clean out the service name
        aws_service_name = (
            aws_service_name.lower().strip().replace(" ", "_").replace("-", "_")
        )
        aws_service_name = hub.tool.format.keyword.unclash(aws_service_name)

        # Get supported operations for this service
        resource_operations = hub.pop_create.aws.service.parse_resource_and_operations(
            service_name=aws_service_name,
            session=session,
        )

        requested_service_resources = hub.OPT.pop_create.service_resources
        if bool(requested_service_resources):
            # if the CLI provides resources, filter the list of resources to process
            # e.g. --service_resources db_cluster db_instance
            resource_operations = {
                r: resource_operations[r]
                for r in requested_service_resources
                if r in resource_operations
            }

        for resource_name, functions in tqdm.tqdm(
            resource_operations.items(), desc="operations"
        ):
            resource_modules = dict()
            # Clean out resource name
            resource_name = (
                resource_name.lower().strip().replace(" ", "_").replace("-", "_")
            )

            # Check if the plugin should be created
            #   - see if it exists
            #   - or --overwrite flag is used
            resource_plugin_exists = hub.pop_create.aws.init.plugin_exists(
                ctx, aws_service_name, resource_name
            )
            should_create_resource_plugin = (
                ctx.overwrite_existing or not resource_plugin_exists
            )

            if should_create_resource_plugin:
                # parse known or commonly used resource actions for the resource
                resource_actions = hub.pop_create.aws.resource.parse_actions(
                    session,
                    aws_service_name,
                    resource_name,
                    functions,
                )

                # create shared resource data to be used when creating resource plugins
                shared_resource_data = {
                    "aws_service_name": aws_service_name,
                    "resource_name": resource_name,
                    # CRUD functions
                    "get": resource_actions.get("get"),
                    "create": resource_actions.get("create"),
                    "update": resource_actions.get("update"),
                    "delete": resource_actions.get("delete"),
                    "list": resource_actions.get("list"),
                    "generic_resource_init_call": hub.pop_create.aws.resource.build_resource_init_call(
                        aws_service_name, resource_name
                    ),
                    "generic_resource_describe_call": hub.pop_create.aws.resource.build_get_by_resource_call(),
                }

                # get resource exec, state, and tool modules
                resource_modules["exec"] = {
                    f"{aws_service_name}.{resource_name}": hub.pop_create.aws.plugin.parse_exec_plugin(
                        ctx, shared_resource_data
                    )
                }

                resource_modules["state"] = {
                    f"{aws_service_name}.{resource_name}": hub.pop_create.aws.plugin.parse_state_plugin(
                        ctx, shared_resource_data
                    )
                }

                resource_modules["tool"] = {
                    f"{aws_service_name}.{resource_name}_utils": hub.pop_create.aws.utils.plugin.parse(
                        shared_resource_data
                    )
                }

                hub.pop_create.aws.init.run_pop_create_resource_modules(
                    ctx, directory, aws_service_name, resource_modules
                )

        # Now create any service related modules
        hub.pop_create.aws.init.run_pop_create_service_modules(
            ctx, directory, aws_service_name, session
        )

    return ctx


def plugin_exists(hub, ctx, aws_service_name: str, resource_name: str) -> bool:
    """
    Validate if the plugin path exists based on create plugin
    """
    path = pathlib.Path(ctx.target_directory).absolute() / ctx.clean_name
    if "auto_state" in ctx.create_plugin:
        path = path / "exec"
    elif "state_modules" in ctx.create_plugin:
        path = path / "states"
    elif "tests" in ctx.create_plugin:
        path = path / "tests" / "integration" / "states"

    path = path / aws_service_name / f"{resource_name}.py"
    if path.exists():
        hub.log.info(f"Plugin already exists at '{path}', use `--overwrite` to modify")
        return True

    return False


def run_pop_create_resource_modules(
    hub, ctx, directory: str, aws_service_name: str, modules: dict
):
    if ctx.create_plugin == "auto_state":
        # create exec and tools
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "auto_state", aws_service_name, modules["exec"]
        )
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "tool", aws_service_name, modules["tool"]
        )
        # TODO: run tests plugin
    elif ctx.create_plugin == "exec_modules":
        # create exec and tools
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "exec_modules", aws_service_name, modules["exec"]
        )
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "tool", aws_service_name, modules["tool"]
        )
        # TODO: run tests plugin
    elif ctx.create_plugin == "state_modules":
        # create exec, state and tools
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "exec_modules", aws_service_name, modules["exec"]
        )
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "state_modules", aws_service_name, modules["state"]
        )
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "tool", aws_service_name, modules["tool"]
        )
        # TODO: tests
    elif ctx.create_plugin == "tool":
        # create tool
        hub.pop_create.aws.init.create_plugin(
            ctx, directory, "tool", aws_service_name, modules["tool"]
        )


def run_pop_create_service_modules(
    hub,
    ctx,
    directory,
    aws_service_name: str,
    session: "boto3.session.Session",
):
    # Get service modules e.g. tag
    service_tag_methods = hub.pop_create.aws.service.parse_service_tag_methods(
        session=session,
        aws_service_name=aws_service_name,
    )

    tag_module = {
        f"{aws_service_name}.tag": hub.pop_create.aws.tag.plugin.parse(
            aws_service_name, service_tag_methods
        )
    }

    hub.pop_create.aws.init.create_plugin(
        ctx, directory, "tool", aws_service_name, tag_module
    )


def create_plugin(
    hub, ctx, directory, create_plugin_name, aws_service_name, plugins: dict
):
    try:
        # Initialize cloud spec and run it with provided create_plugin
        ctx.cloud_spec = NamespaceDict(
            api_version="",
            project_name=ctx.project_name,
            service_name=ctx.service_name,
            request_format=hub.pop_create.aws.init.resolve_plugin_request_format(
                create_plugin_name
            ),
            plugins=plugins,
        )

        hub.cloudspec.init.run(
            ctx,
            directory,
            create_plugins=[create_plugin_name],
        )
    finally:
        hub.log.info(
            f"Finished creating modules for service [{aws_service_name}] with create plugin {create_plugin_name}]"
        )
        # Reset it for the next resource or plugin
        ctx.cloud_spec = None


def resolve_plugin_request_format(hub, create_plugin_name):
    request_format = {}
    if create_plugin_name == "auto_state" or create_plugin_name == "exec_modules":
        request_format = {
            "get": hub.pop_create.aws.template.GET_REQUEST_FORMAT,
            "create": hub.pop_create.aws.template.CREATE_REQUEST_FORMAT,
            "delete": hub.pop_create.aws.template.DELETE_REQUEST_FORMAT,
            "update": hub.pop_create.aws.template.UPDATE_REQUEST_FORMAT,
            "list": hub.pop_create.aws.template.LIST_REQUEST_FORMAT,
        }
    elif create_plugin_name == "state_modules":
        request_format = {
            "present": hub.pop_create.aws.template.PRESENT_REQUEST_FORMAT,
            "absent": hub.pop_create.aws.template.ABSENT_REQUEST_FORMAT,
            "describe": hub.pop_create.aws.template.DESCRIBE_REQUEST_FORMAT,
        }
    elif create_plugin_name == "tool":
        request_format = {
            "get_tags_for_resource": hub.pop_create.aws.tag.template.GET_TAGS_FOR_RESOURCE_REQUEST,
            "update_tags": hub.pop_create.aws.tag.template.UPDATE_TAGS_REQUEST,
            "convert_raw_resource_to_present_async": hub.pop_create.aws.utils.template.CONVERT_RAW_RESOURCE_TO_PRESENT_REQUEST,
        }

    return request_format
