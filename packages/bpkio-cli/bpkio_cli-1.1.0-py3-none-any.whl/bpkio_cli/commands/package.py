import json
import logging
import random
import string

import click
import cloup
from bpkio_api.models.common import summary
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from bpkio_cli.core.app_settings import AppContext
from bpkio_cli.core.packager import PackageInstaller, ResourcePackager

logger = logging.getLogger(__name__)


@cloup.group(aliases=["pkg"], help="Work with reusable packages of resources")
def package():
    pass


@package.command(help="Make a package of resources")
@cloup.argument(
    "ref",
    help="A reference to an item or list in the CLI register",
    default="$",
    required=False,
)
@cloup.option("-o", "--output", type=click.File("w"), required=False, default=None)
@click.pass_obj
def make(obj: AppContext, ref: str, output):
    if ref == "$":
        resources = inquirer.checkbox(
            message="What (top-level) resources do you want to include in the package?  ",
            choices=[
                Choice(s, name=summary(s, with_class=True), enabled=(i == 0))
                for i, s in enumerate(obj.cache.list_resources())
            ],
        ).execute()

    if ref == "@":
        list = inquirer.select(
            message="What list of resources to use?  ",
            multiselect=False,
            choices=[
                Choice(lst, name=k, enabled=(i == 0))
                for i, (k, lst) in enumerate(obj.cache.list_lists().items())
            ],
        ).execute()

        resources = inquirer.checkbox(
            message="What (top-level) resources do you want to include in the package?  ",
            choices=[Choice(s, name=summary(s, with_class=True)) for s in list],
        ).execute()

    if resources:
        package_resources(resources, obj.api, output)


def package_resources(resources, api, output: click.File):
    packager = ResourcePackager(api)
    pkg = packager.package(root_resources=resources)

    if output:
        output.write(json.dumps(pkg, indent=2))
        logger.info(f"Package stored into {output.name}")
    else:
        print(json.dumps(pkg, indent=2))


@package.command(help="Deploy a package")
@cloup.argument(
    "file",
    type=click.File("r"),
    help="JSON File containing the package",
    required=True,
)
@cloup.option(
    "--duplicate",
    type=str,
    help="Create duplicates of any resource that supports it,"
    " by adding a unique extension to the resource name",
    is_flag=False,
    flag_value="random",
    default=None,
)
@click.pass_obj
def deploy(obj: AppContext, file, duplicate):
    if duplicate == "random":
        duplicate = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    if duplicate:
        duplicate = f"({duplicate})"

    installer = PackageInstaller(obj.api, name_suffix=duplicate)

    package = json.load(file)

    output = installer.deploy(package)

    table = [
        dict(
            status=installer.statuses[st],
            resource=summary(res, with_class=True),
            message=msg,
        )
        for (res, st, msg) in output.values()
    ]

    obj.response_handler.treat_simple_list(table)
