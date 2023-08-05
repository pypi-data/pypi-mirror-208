# from __future__ import absolute_import

import logging

import click
import cloup

import bpkio_cli.commands as commands
from bpkio_cli.commands.configure import init
from bpkio_cli.core.initialize import initialize
from bpkio_cli.core.logger import (
    get_child_logger,
    get_level_names,
    set_console_logging_level,
)
from bpkio_cli.writers.breadcrumbs import display_tenant_info

logger = get_child_logger("cli")

LOG_LEVEL = None
LOG_SDK = False


SETTINGS = cloup.Context.settings(
    formatter_settings=cloup.HelpFormatter.settings(theme=cloup.HelpTheme.dark())
)


@cloup.group(show_subcommand_aliases=True, context_settings=SETTINGS)
@click.version_option(
    package_name="bpkio_cli", prog_name="Command Line helpers for broadpeak.io"
)
@click.option("-t", "--tenant", help="Identifier of the tenant profile to impersonate")
@click.option(
    "--log-level",
    type=click.Choice(get_level_names()),
    required=False,
    help="Set the log level",
)
@click.option(
    "--log-sdk",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
    help="Log messages from the underlying API client",
)
@click.option(
    "-cc / -nc",
    "--cache / --no-cache",
    "use_cache",
    is_flag=True,
    default=True,
    help="Enable or disable resource caches (enabled by default)",
)
@click.option(
    "--breadcrumbs / --no-breadcrumbs",
    "display_breadcrumbs",
    is_flag=True,
    default=True,
    help="Display or hide information about the resources accessed (enabled by default)",
)
@click.pass_context
def cli(ctx, tenant, log_level, log_sdk, use_cache, display_breadcrumbs):
    if log_level or LOG_LEVEL:
        set_console_logging_level(
            log_level or LOG_LEVEL, include_sdk=log_sdk or LOG_SDK
        )

    # Bypass initialisation if there is an explicit call to initialise the configuration
    if ctx.invoked_subcommand not in ["init", "config"]:
        app_context = initialize(tenant, use_cache, get_tenant_info=display_breadcrumbs)

        if display_breadcrumbs:
            display_tenant_info(app_context.tenant)

        # TODO - validate the token in the initialisation of BroadpeakApi
        ctx.obj = app_context

    @ctx.call_on_close
    def close_cleanly():
        try:
            app_context.cache.save()
        except Exception as e:
            pass


cli.section("Configuration", commands.hello, init, commands.configure)

commands.add_sources_section(cli)
commands.add_services_section(cli)

cli.section(
    "Account resources",
    commands.add_tenants_commands(),
    commands.add_users_commands(),
    commands.consumption,
)

cli.section(
    "Other resources",
    commands.profile,
)

cli.section("Advanced", commands.url, commands.memory, commands.package)


def debug_entry_point():
    global LOG_LEVEL
    LOG_LEVEL = logging.DEBUG
    global LOG_SDK
    LOG_SDK = True
    cli(obj={})


def safe_entry_point():
    try:
        cli()
    except Exception as e:
        if hasattr(e, "status_code"):
            st = " [{}] ".format(e.status_code)
        else:
            st = ""
        msg = "{}:{}{}".format(e.__class__.__name__, st, e)
        click.secho(msg, fg="red")

        if hasattr(e, "original_message"):
            click.secho("  > " + e.original_message, fg="red")


if __name__ == "__main__":
    debug_entry_point()
