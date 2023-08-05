import re

import click
import cloup
from bpkio_api.api import DEFAULT_FQDN, BroadpeakIoApi
from bpkio_api.credential_provider import TenantProfileProvider
from InquirerPy import inquirer

from bpkio_cli.commands.hello import hello
from bpkio_cli.core.initialize import initialize
from bpkio_cli.core.response_handler import ResponseHandler
from bpkio_cli.utils.config_provider import ConfigProvider


# Command: INIT
# To be attached to the root group
@cloup.command(help="Initialize the tool, and create a first tenant profile")
@click.pass_context
def init(ctx):
    cp = TenantProfileProvider()

    if not cp.has_default_tenant():
        ctx.invoke(add)

    click.secho("All done!  You're ready to go now", fg="yellow")


# Group: CONFIG
@cloup.group(
    aliases=["config", "cfg"],
    help="Configure how the CLI works",
    show_subcommand_aliases=True,
)  # type: ignore
@click.pass_obj
def configure(obj):
    pass


# Command: SET
@configure.command(help="Set a configuration option")
@click.argument("key", required=True)
@click.argument("value", required=True)
def set(key, value):
    cp = ConfigProvider()
    cp.set_config(key, value)


# Group: TENANTS
@configure.group(
    aliases=["tenant", "tnt"],
    help="Define CLI credential profiles to be able to easily switch tenant",
)
@click.pass_obj
def tenants(obj):
    pass


# Command: LIST
@tenants.command(help="List the tenants previously configured", aliases=["ls"])
def list():
    cp = TenantProfileProvider()
    tenants = cp.list_tenants()
    ResponseHandler().treat_list_resources(
        resources=tenants, select_fields=["label", "id", "fqdn"]
    )


# Command: SWITCH
@tenants.command(help="Switch the tenant used for subsequent invocations")
@click.argument("tenant", required=False)
@click.pass_context
def switch(ctx, tenant):
    if not tenant:
        cp = TenantProfileProvider()
        tenant_list = cp.list_tenants()
        choices = [dict(value=t.label, name=f"{t.label} ({t.id})") for t in tenant_list]

        tenant = inquirer.fuzzy(message="Select a tenant", choices=choices).execute()

    # Write it to the .tenant file
    with open(".tenant", "w") as f:
        f.write(tenant)

    # Reinitialize the app context, before showing tenant info to the user for validation
    ctx.obj = initialize(tenant)
    ctx.invoke(hello)


# Command: ADD
@tenants.command(help="Store credentials for a new tenant")
def add():
    cp = TenantProfileProvider()

    api_key = inquirer.secret(
        message="API Key for the Tenant: ",
        validate=lambda candidate: BroadpeakIoApi.is_valid_api_key_format(candidate),
        invalid_message="Invalid API Key",
    ).execute()
    fqdn = inquirer.text(
        message="Application domain name",
        default=DEFAULT_FQDN,
        validate=lambda url: BroadpeakIoApi.is_correct_entrypoint(url, api_key),
        invalid_message=(
            "This URL does not appear to be a broadpeak.io application, "
            "or your API key does not give you access to it"
        ),
    ).execute()

    # Test the API key by initialising the API with it
    bpk_api = BroadpeakIoApi(api_key=api_key, fqdn=fqdn)

    # Parse the API
    tenant = bpk_api.get_self_tenant()
    tenant_id = tenant.id

    default_name = tenant.name
    default_name = re.sub(r"[^a-zA-Z0-9-_]", "_", default_name)
    # If there is no default profile yet, suggest that one instead
    if not cp.has_default_tenant():
        default_name = "default"

    # key = click.prompt("Profile name", type=str, default=default_name)
    key = inquirer.text(
        message="Profile name",
        default=default_name,
        validate=lambda s: bool(re.match(r"^[a-zA-Z0-9_-]*$", s)),
        invalid_message="Please only use alphanumerical characters",
    ).execute()

    # Create a dict
    config = {"api_key": api_key, "id": tenant.id}

    if fqdn != DEFAULT_FQDN:
        config["fqdn"] = fqdn

    cp.add_tenant(key, config)

    click.echo(
        f'A profile named "{key}" for tenant {tenant_id} has been added to {cp.inifile}'
    )
    if key != "default":
        click.echo(
            f"You can now simply use `bic --tenant {key} COMMAND` to work within that tenant's account"
        )
    else:
        click.echo(
            "You can now simply use `bic COMMAND` to work within that tenant's account"
        )


# Command: EDIT
@tenants.command(help="Edit the tenant credential file manually")
def edit():
    cp = TenantProfileProvider()
    click.launch(str(cp.inifile))
