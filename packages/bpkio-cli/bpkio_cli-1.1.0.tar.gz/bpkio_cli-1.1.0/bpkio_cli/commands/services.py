import click
import cloup
from bpkio_api.models import (
    AdInsertionService,
    ContentReplacementService,
    ContentReplacementSlot,
    ServiceSparse,
    VirtualChannelService,
    VirtualChannelSlot,
)
from bpkio_cli.commands.services_create import create_ad_insertion_service_command

from bpkio_cli.commands.template_crud import create_resource_group
from bpkio_cli.commands.template_crud_slots import create_child_resource_group
from bpkio_cli.core.app_settings import AppContext

default_fields = ["id", "name", "type", "serviceId", "format"]


def add_services_section(cli):
    root_endpoint = "services"
    root: cloup.Group = create_resource_group(
        "service",
        resource_class=ServiceSparse,
        endpoint_path=[root_endpoint],
        aliases=["svc", "services"],
        with_content_commands=["all"],
        default_fields=default_fields,
    )

    return cli.section(
        "Services",
        root,
        create_resource_group(
            "content-replacement",
            resource_class=ContentReplacementService,
            endpoint_path=[root_endpoint, "content_replacement"],
            aliases=["cr"],
            default_fields=default_fields,
            with_content_commands=["all"],
            extra_commands=[
                add_slots_commands(
                    resource_class=ContentReplacementSlot,
                    parent_path=[root_endpoint, "content_replacement"],
                    default_fields=[
                        "id",
                        "name",
                        "relativeStartTime",
                        "relativeEndTime",
                        "duration",
                        "replacement.id",
                        "replacement.name",
                    ],
                )
            ],
        ),
        create_resource_group(
            "ad-insertion",
            resource_class=AdInsertionService,
            endpoint_path=[root_endpoint, "ad_insertion"],
            aliases=["dai", "ssai"],
            default_fields=["id", "name", "type", "sub_type", "serviceId", "format"],
            with_content_commands=["all"],
            extra_commands=[create_ad_insertion_service_command()]
        ),
        create_resource_group(
            "virtual-channel",
            resource_class=VirtualChannelService,
            endpoint_path=[root_endpoint, "virtual_channel"],
            aliases=["vc"],
            default_fields=default_fields,
            with_content_commands=["all"],
            extra_commands=[
                add_slots_commands(
                    resource_class=VirtualChannelSlot,
                    parent_path=[root_endpoint, "virtual_channel"],
                    default_fields=[
                        "id",
                        "name",
                        "type",
                        "relativeStartTime",
                        "relativeEndTime",
                        "duration",
                        "replacement.id",
                        "replacement.name",
                    ],
                )
            ],
        ),
    )


def add_slots_commands(resource_class, parent_path, default_fields):
    return create_child_resource_group(
        "slot",
        resource_class=resource_class,
        endpoint_path=parent_path + ["slots"],
        aliases=["slots"],
        default_fields=default_fields,
    )

