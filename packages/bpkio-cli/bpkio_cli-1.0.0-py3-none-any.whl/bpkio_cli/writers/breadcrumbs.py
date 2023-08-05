import click
from bpkio_api import DEFAULT_FQDN


def display_resource_info(resource):
    core_info = "{} {}".format(resource.__class__.__name__, resource.id)
    name = resource.name if hasattr(resource, 'name') else ""

    info = "[{c}]  {n}".format(c=core_info, n=name)

    click.secho(info, err=True, fg="white", bg="blue", dim=False)


def display_tenant_info(tenant):
    info = "[Tenant {i}] - {n}".format(i=tenant.id, n=tenant.name)
    if url := tenant._fqdn:
        if url != DEFAULT_FQDN:
            info = info + f" - ({url})"

    click.secho(info, err=True, fg="green", bg="blue", dim=False)
