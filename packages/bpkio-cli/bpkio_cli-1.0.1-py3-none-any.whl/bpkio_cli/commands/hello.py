import click

from bpkio_cli.core.app_settings import AppContext


# Command: HELLO
@click.command()
@click.pass_obj
def hello(obj: AppContext):
    """Validate access to the API and display tenant information"""

    tenant = obj.api.get_self_tenant()
    candidate_users = obj.api.users.search(field="tenantId", value=tenant.id)
    candidate_users.sort(key=lambda u: u.creationDate)
    user = candidate_users[0]

    click.echo(f'You are working with tenant "{tenant.name}"  [id: {tenant.id}]')
    click.echo(
        f'The first user in that account is "{user.firstName}"  [email: {user.email}]'
    )
    if not obj.api.uses_default_fqdn():
        click.echo(
            f"This tenant is using a non-default API entrypoint at {obj.api._fqdn}"
        )
