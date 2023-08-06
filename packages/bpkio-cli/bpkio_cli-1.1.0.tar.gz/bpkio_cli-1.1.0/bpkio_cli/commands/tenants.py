from bpkio_cli.commands.template_crud import create_resource_group
from bpkio_api.models import Tenant


def add_tenants_commands():
    return create_resource_group(
        "tenant",
        resource_class=Tenant,
        endpoint_path=["tenants"],
        aliases=["tnt", "tenants"],
        default_fields=["id", "name"],
    )
