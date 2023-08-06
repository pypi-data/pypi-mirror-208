import re
from urllib.parse import urlparse, urlunparse

import click
import cloup
from bpkio_api.helpers.source_type import SourceTypeDetector
from bpkio_api.models import (
    AdServerSource,
    AdServerSourceIn,
    AssetCatalogSource,
    AssetCatalogSourceIn,
    AssetSource,
    AssetSourceIn,
    LiveSource,
    LiveSourceIn,
    SlateSource,
    SlateSourceIn,
    SourceSparse,
    SourceType,
)
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from bpkio_cli.commands.template_crud import create_resource_group
from bpkio_cli.core.app_settings import AppContext


# COMMAND: CREATE
@cloup.command(
    help="Create a Source from just a URL. "
    "The CLI will work out what type of Source it is and create it accordingly"
)
@cloup.argument("url", help="URL of the source", required=False)
@click.pass_obj
def create(obj: AppContext, url: str):
    if not url:
        url = inquirer.text(
            message="URL of the source",
            validate=lambda url: re.match(r"^https?://", url.strip()),
            invalid_message=("Your URL must be a valid HTTP URL"),
        ).execute()

    source_type = SourceTypeDetector.determine_source_type(url)
    if not source_type:
        raise Exception("Could not determine the type of source for that URL")

    click.secho("This appears to be a source of type: %s" % source_type.value)

    if source_type == SourceType.ASSET:
        source_type = inquirer.select(
            message="From this, create:",
            choices=[
                Choice(SourceType.ASSET, name="Asset"),
                Choice(SourceType.ASSET_CATALOG, name="Asset Catalog"),
            ],
            multiselect=False,
        ).execute()

    if source_type == SourceType.ASSET_CATALOG:
        url_parts = urlparse(url)
        path_parts = url_parts.path.split("/")[1:-1]
        paths = []
        last_path = ""
        for p in path_parts:
            last_path = last_path + "/" + p
            paths.append(last_path + "/")

        common_path = inquirer.select(
            message="Common path for all assets:",
            choices=paths,
            multiselect=False,
        ).execute()

        new_url = url_parts._replace(path=common_path, query="")
        new_url = urlunparse(new_url)

        sample = url.replace(new_url, "")

    name = inquirer.text(message="Name for the source").execute()

    match source_type:
        case SourceType.LIVE:
            source = obj.api.sources.live.create(LiveSourceIn(name=name, url=url))
        case SourceType.AD_SERVER:
            parts = url.split("?")
            if len(parts) == 1:
                parts.append("")
            source = obj.api.sources.ad_server.create(
                AdServerSourceIn(name=name, url=parts[0], queries=parts[1])
            )
        case SourceType.SLATE:
            source = obj.api.sources.slate.create(SlateSourceIn(name=name, url=url))
        case SourceType.ASSET:
            source = obj.api.sources.asset.create(AssetSourceIn(name=name, url=url))
        case SourceType.ASSET_CATALOG:
            source = obj.api.sources.asset_catalog.create(
                AssetCatalogSourceIn(name=name, url=new_url, assetSample=sample)
            )
        case _:
            raise click.BadArgumentUsage("Unrecognised source type '%s'" % source_type)

    obj.response_handler.treat_single_resource(source)


def add_sources_section(cli):
    root_endpoint = "sources"
    root: cloup.Group = create_resource_group(
        "source",
        resource_class=SourceSparse,
        endpoint_path=[root_endpoint],
        aliases=["src", "sources"],
        with_content_commands=["all"],
        default_fields=["id", "name", "type", "format", "url"],
    )

    root.add_command(create)

    return cli.section(
        "Sources",
        root,
        create_resource_group(
            "asset",
            resource_class=AssetSource,
            endpoint_path=[root_endpoint, "asset"],
            aliases=["assets"],
            default_fields=["id", "name", "format", "url"],
            with_content_commands=["url", "check", "table", "read", "play", "profile"],
        ),
        create_resource_group(
            "live",
            resource_class=LiveSource,
            endpoint_path=[root_endpoint, "live"],
            with_content_commands=["all"],
            default_fields=["id", "name", "format", "url", "profile"],
        ),
        create_resource_group(
            "asset-catalog",
            resource_class=AssetCatalogSource,
            endpoint_path=[root_endpoint, "asset_catalog"],
            aliases=["catalog", "catalogs"],
            default_fields=["id", "name", "url"],
            with_content_commands=["url", "check", "table", "read", "play", "profile"],
        ),
        create_resource_group(
            "ad-server",
            resource_class=AdServerSource,
            endpoint_path=[root_endpoint, "ad_server"],
            aliases=["ads"],
            with_content_commands=["url", "check", "table", "read"],
            default_fields=["id", "name", "url"],
        ),
        create_resource_group(
            "slate",
            resource_class=SlateSource,
            endpoint_path=[root_endpoint, "slate"],
            aliases=["slates"],
            default_fields=["id", "name", "format", "url"],
            with_content_commands=["url", "check", "play"],
        ),
    )
