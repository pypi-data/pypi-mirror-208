from bpkio_api.models import User

from bpkio_cli.commands.template_crud import create_resource_group


def add_users_commands():
    return create_resource_group(
        "user",
        resource_class=User,
        endpoint_path=["users"],
        aliases=["usr", "users"],
        default_fields=["id", "firstName", "lastName", "email", "tenantId"],
    )
