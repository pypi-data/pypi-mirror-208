import click
import cloup
from bpkio_api.helpers.handlers import ContentHandler, factory
from bpkio_api.helpers.source_type import SourceTypeDetector
from bpkio_api.models import SourceType
from pydantic import HttpUrl, parse_obj_as

import bpkio_cli.options as bic_options
from bpkio_cli.click_mods import ApiResourceGroup
from bpkio_cli.commands.sources import create as source_create
from bpkio_cli.core.app_settings import AppContext
from bpkio_cli.utils.config_provider import ConfigProvider
from bpkio_cli.utils.profile_maker import make_transcoding_profile
from bpkio_cli.writers.content_display import display_content
from bpkio_cli.writers.players import StreamPlayer
from bpkio_cli.writers.tables import display_table


def determine_source_type(full_url) -> SourceType | None:
    source_type = SourceTypeDetector.determine_source_type(full_url)
    if not source_type:
        click.secho(
            "Could not determine the type of source for that URL", fg="red", bold="true"
        )
        return None
    else:
        return source_type


def get_handler(sub: int | None = None) -> ContentHandler:
    ctx = click.get_current_context()
    url = ctx.obj.resources.last()

    handler: ContentHandler = factory.create_handler(url)

    if not sub:
        return handler
    else:
        if not handler.has_children():
            raise click.UsageError(
                "`--sub` cannot be used with this source, as it has no children URLs"
            )
        return handler.get_child(sub)


# Group: URLs
@cloup.group(
    cls=ApiResourceGroup, help="Work directly with URLs", resource_class=HttpUrl
)
@cloup.argument(
    "full_url",
    help=("The URL to work with"),
)
@click.pass_obj
def url(obj: AppContext, full_url: HttpUrl):
    full_url = parse_obj_as(HttpUrl, full_url)
    obj.cache.record(full_url)


# Command: GET
@cloup.command(help="Get details about a URL")
@click.pass_obj
def get(obj: AppContext):
    full_url = obj.resources.last()
    source_type = determine_source_type(full_url)

    click.secho("This appears to be a source of type: %s" % source_type.value)


# Command: CHECK
@cloup.command(help="Checks the validity of a URL")
@bic_options.json
@bic_options.list()
@click.pass_obj
def check(obj: AppContext, select_fields, sort_fields, json):
    full_url = obj.resources.last()
    source_type = determine_source_type(full_url)

    if source_type:
        results = obj.api.sources.check(type=source_type, url=full_url)

        obj.response_handler.treat_list_resources(
            results, json=json, select_fields=select_fields, sort_fields=sort_fields
        )


# --- READ Command
@cloup.command(
    help="Loads and displays the content of a URL"
    ", optionally highlighted with relevant information"
)
@bic_options.read
@bic_options.url
@bic_options.table
def read(sub: int, table: bool, raw: bool, top: bool, tail: bool, **kwargs):
    handler = get_handler(sub)

    display_content(
        handler=handler,
        max=1,
        interval=0,
        table=table,
        raw=raw,
        top=top,
        tail=tail,
    )


# --- POLL Command
@cloup.command(help="Similar to `read`, but regularly re-load the URL's content")
@bic_options.read
@bic_options.url
@bic_options.poll
@bic_options.table
def poll(
    sub: int,
    max: int,
    interval: int,
    raw: bool,
    diff: bool,
    top: bool,
    tail: bool,
    clear: bool,
    table: bool,
    **kwargs,
):
    handler = get_handler(sub)

    display_content(
        handler=handler,
        max=max,
        interval=interval,
        table=table,
        raw=raw,
        diff=diff,
        top=top,
        tail=tail,
        clear=clear,
    )


# --- PLAY Command
@cloup.command(help="Open the URL in a web player", aliases=["open"])
@click.option(
    "-s",
    "--sub",
    type=int,
    default=None,
    help="For HLS, reads a sub-playlist (by index - "
    "as given by the `read ID --table` option with the main playlist)",
)
@click.option(
    "-p",
    "--player",
    default="CONFIG",
    help="The template for a player URL",
    type=str,
    is_flag=False,
    flag_value="CHOICE",
)
def play(sub: int, player: str):
    handler = get_handler(sub)

    if player == "CONFIG":
        player = ConfigProvider().get("player")

    if player == "CHOICE":
        player = StreamPlayer.prompt_player()

    StreamPlayer().launch(url=handler.url, template=player, name="")


# --- CREATE Command
@cloup.command(help="Create a Source from the URL")
@click.pass_context
def store(ctx):
    full_url = ctx.obj.resources.last()

    ctx.invoke(source_create, url=full_url)


# --- PROFILE Command
@cloup.command(help="Create a Transcoding Profile from the content of the URL")
@click.option(
    "--table/--no-table",
    "with_table",
    is_flag=True,
    default=False,
    help="Add or hide summary information about the content of the resource",
)
@click.pass_obj
def profile(obj: AppContext, with_table: bool):
    handler = get_handler()

    profile = make_transcoding_profile(handler)

    if with_table:
        display_table(profile["transcoding"]["jobs"])
    else:
        obj.response_handler.treat_single_resource(profile, json=True)


url.add_section(
    cloup.Section("Content Commands", [check, get, read, poll, play, profile])
)

url.add_section(cloup.Section("Other Commands", [store]))
