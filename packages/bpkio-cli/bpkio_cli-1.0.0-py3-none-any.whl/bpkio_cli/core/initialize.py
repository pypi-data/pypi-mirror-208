from bpkio_api import BroadpeakIoApi
from bpkio_api.credential_provider import TenantProfileProvider
from bpkio_api.models import BaseResource

from bpkio_cli.core.app_settings import AppContext
from bpkio_cli.core.logger import get_child_logger

logger = get_child_logger("init")


def initialize(
    tenant: str | int | None = None,
    use_cache: bool = True,
    get_tenant_info: bool = True,
) -> AppContext:
    """Function that initialises the CLI

    If a tenant label or ID is provided, the CLI will be initialised for that tenant.
    Otherwise, the CLI will be initialised with the last tenant used (and stored in
    a `.tenant` file).

    Successful initialisation requires that there is a profile in ~/.bpkio/tenants
    for that tenant.

    Args:
        tenant (str | int): Name of the CLI profile or ID of the tenant

    Raises:
        click.Abort: if no tenant profile could be found in the ~/.bpkio/tenants file

    Returns:
        AppContext: The config for the app
    """
    if not tenant:
        try:
            with open(".tenant") as f:
                tenant = f.read().strip()
                logger.debug(f"File '.tenant' contains label '{tenant}'")
        except Exception:
            tenant = None
    else:
        tenant = str(tenant)

    # tenant_provider = TenantProfileProvider()
    # tenant_profile = tenant_provider.get_tenant_profile(tenant)
    # try:
    #     api_key = tenant_profile.api_key  # type: ignore
    # except Exception as e:
    #     click.secho(e.args[0], fg="red")
    #     click.secho("You may want to try `bic init` first...\n", fg="yellow")
    #     raise click.Abort
    #
    # fqdn = tenant_profile.fqdn  # type: ignore
    # logger.debug("FQDN for this tenant: %s" % fqdn)

    api = BroadpeakIoApi(tenant=tenant, use_cache=use_cache)
    app_context = AppContext(
        api=api,
        tenant_provider=TenantProfileProvider(),
    )

    if get_tenant_info:
        full_tenant = api.get_self_tenant()
        app_context.tenant = full_tenant
    else:
        app_context.tenant = BaseResource(id=api.get_tenant_id())

    return app_context
